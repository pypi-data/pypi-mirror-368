#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Summer 2023, BRACE2 Team
#   Berkeley, CA
#
#----------------------------------------------------------------------------#
"""
0. dd = {event_id: {idx01: mode01, idx02: mode02}} // with mode0? = {node: [*ndf]}
                                                   // or   mode0? = [*ndf] ?
                                                   // mode = {"period", "idx", "shape"}
1. aa = {event_id: mode}
2. for event in aa:
      bb[event] = 0.0
      for other_event in aa:
        if other_event != event :
            if assoc(dd[event], dd[other_event])[event] == event:
                bb[event] += 1/(len(aa)-1)

"""

import numpy as np
from irie.apps.evaluation.models import Evaluation

def mkdd(asset, pid, key):
    evaluations = list(reversed(sorted(Evaluation.objects.filter(asset=asset),
                                  key=lambda x: x.event.motion_data["event_date"])))
    return {
            i_eval: {
                idx: mode for idx,mode in \
                     enumerate(evaluation.evaluation_data["SPECTRAL_SHIFT_IDENTIFICATION"]["summary"][pid])
                        if key in mode and mode.get("emac", 1.0) > 0.5 and mode.get("mpc", 1.0) > 0.5

            } for i_eval,evaluation in enumerate(evaluations)
    }

def _ssid_stats(asset, pid, key):
    filtered_modes = mkdd(asset, pid, key)
    values = [mode[key] for mode in event.values() for event in filtered_modes.values()]

    mean = np.mean(values)
    std =  np.std(values)

    result = {}
    for i_eval, event_results in filtered_modes.items():
        idx = np.argmin(np.abs(mean - np.array([mode[key] for mode in event_results])))
        result[i_eval] = event_results[idx]
        result[i_eval]["idx"] = idx
    return result

#   return {
#           i_eval: event_results[np.argmin(np.abs(mean - np.array([mode[key] for mode in event_results])))]
#               if event_results and len(event_results) > 0 else {}
#         for i_eval, event_results in filtered_modes.items()
#   }


def ff(asset, pid, key):
    # evaluation_data 
    dd = mkdd(asset, pid, key)

    aa = _ssid_stats(asset, pid, key)

    for event in aa:
        aa[event]["bb"] = 0.0
        for other_event in aa:
            if other_event != event :
                if assoc(dd[event], dd[other_event])[event] == event:
                    aa[event]["bb"] += 1/(len(aa)-1)

HELP = """
modeID [options] <baseline> <unknown>

OeventPTIONS:
    -c<compare-mode>        compare mode, currently only 'max' supported

EXAMPLES:

Default compare:
    modeID baseline.yaml unknown.yaml

To use `max` compare mode:
    modeID -cmax baseline.yaml unknown.yaml
or
    modeID -c max baseline.yaml unknown.yaml

"""

import yaml
import numpy as np
import sys

TOL = 1e-14

def _clean_modes(modes, tol=1e-14):
    "Zero-out small values"
    mode_array = np.array([
        [val for node in mode.values() for val in node]
             for mode in modes.values()
    ])
    mode_array[abs(mode_array) < tol] = 0.0
    return mode_array


def associate_modes(baseline, unidentified_dict, compare = None, verbose=True):
    identified_keys = set()
    identified = {}
    _old_labels = list(unidentified_dict.keys())

    if compare is None:
        _compare = lambda errors, labels: np.argmin(errors)

    elif compare == "max":
        _compare = lambda errors, labels: np.argmax(errors[~np.isin(np.arange(len(errors)), labels)])

    unidentified = _clean_modes(unidentified_dict, tol=TOL)

    for key, mode in baseline.items():
        #
        baseline_data = np.array([*mode.values()]).flatten()
        baseline_data[abs(baseline_data) < TOL] = 0.0
        scale_index = np.argmax(np.absolute(baseline_data))
        baseline_scale = baseline_data[scale_index]

        errors = np.sum(abs(baseline_data - unidentified*baseline_scale/unidentified[:,scale_index][:,None]), axis=1)

        # Get index of mode from <unidentified> that is closest to `mode`
        index = _compare(errors, identified_keys)
        old_label = _old_labels[index]

        if verbose:
            print(f"{old_label} -> {key}", file=sys.stderr)

        if  old_label in identified_keys and verbose:
            print(f"WARNING: duplicate identification of key {old_label}", file=sys.stderr)

        identified_keys.add(_old_labels[index])
        identified[key] = unidentified[index]

    return identified


if __name__ == "__main__":
    # Parse command line
    index = 1
    compare_mode = None
    if "-c" in sys.argv[1]:
        index += 1
        if len(sys.argv[1]) > 2:
            compare_mode = sys.argv[1][2:]
        else:
            compare_mode = sys.argv[index]
            index += 1

    baseline_file, unidentified_file = sys.argv[index:]


    # Open Files
    with open(unidentified_file, "r") as f:
        unidentified = yaml.load(f, Loader=yaml.Loader)

    with open(baseline_file, "r") as f:
        baseline = yaml.load(f, Loader=yaml.Loader)

    for nodes in unidentified.values():
        node_names = list(nodes.keys())
        break

    # print(yaml.dump(
    #     {
    #         key: {
    #             node_name: [float(v) for v in node_vals] 
    #               for node_name, node_vals in 
    #                  zip(node_names, mode.reshape((-1, len(node_names))).T)
    #         } for key, mode in 
    #         associate_modes(baseline, unidentified, compare=compare).items()
    #     }
    # ))

    # for k,mode in associate_modes(baseline, unidentified, compare=compare).items():
    #     print(f"{k}:\n\t")
    #     print("\n\t".join((f"{node_name}: [{','.join(str(v) for v in node_vals)}]"
    #               for node_name, node_vals in 
    #                  zip(node_names, mode.reshape((-1, len(node_names))).T)
    #     )))

    associate_modes(baseline, unidentified, compare=compare_mode)

