#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
import os.path
import shutil
import tqdm
import sys, json
import zipfile
from pathlib import Path
import contextlib
try:
    from xcsi.csi import collect_outlines, load as load_csi
    from xcsi.csi._frame.section import create_section, iter_sections
    from xcsi.job import Job
    from xcsi.metrics import PeakDrift
except:
    from openbim.csi import load as load_csi, collect_outlines
    from openbim.csi._frame.section import create_section, iter_sections


from irie.apps.prediction.runners import (Runner, RunID, classproperty)

from .utilities import read_model
from .metrics import (
     accel_response_history_plot,
     column_strain_state_metric,
     peak_acceleration_metric,
     peak_drift_metric
)

OPENSEES = [
    sys.executable, "-m", "opensees",
]


def _create_excitation(model, predictor, inputs, dt):
    import numpy as np
    # rotation = predictor.config["orientation"]
    rotation = np.eye(3)*150
    i = 1
    for sensor in predictor.sensorassignment_set.all():
        if sensor.role == "input":
            for dof in range(3):
                series = sum(ai*dx
                            for ai, dx in zip(np.array(inputs[sensor.id]["series"]), rotation[dof]))

                model.timeSeries("Path", i, dt=dt, values=series.tolist())
                model.pattern("UniformExcitation", i, dof+1, accel=i)
                i += 1


def _analyze_and_render(model, artist, nt, dt):
    import veux, veux.motion
    motion = veux.motion.Motion(artist)
    for i in tqdm.tqdm(range(nt)):
        if model.analyze(1, dt) != 0:
            return -1
        motion.advance(i*dt)
        motion.draw_sections(position=lambda x: [1000*u for u in model.nodeDisp(x)],
                             rotation=model.nodeRotation)
        
    motion.add_to(artist.canvas)
    return 0
    


@contextlib.contextmanager
def new_cd(x):
    d = os.getcwd()
    # This could raise an exception, but it's probably
    # best to let it propagate and let the caller
    # deal with it, since they requested x
    os.chdir(x)

    try:
        yield

    finally:
        # This could also raise an exception, but you *really*
        # aren't equipped to figure out what went wrong if the
        # old working directory can't be restored.
        os.chdir(d)


class OpenSeesRunner(Runner):
    @property
    def platform(self):
        return self.conf.get("platform", "xara")


    @classmethod
    def create(cls, asset, request):
        from irie.apps.prediction.models import PredictorModel
        predictor = PredictorModel()
        data = json.loads(request.body)
        # TODO
        data.pop("file")
        uploaded_file = request.FILES.get('config_file', None)
        if uploaded_file:
            with open(uploaded_file.name, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

        # predictor.config_file = uploaded_file # data.pop("file")
        predictor.name = data.pop("name")
        predictor.config = data
        predictor.asset = asset
        predictor.protocol = "IRIE_PREDICTOR_V1"
        predictor.active = True
        return predictor

    @classproperty
    def schema(cls):
        from . import schemas

        return {
            "title": "Structural Model",
            "options": {"disable_collapse": True},
            "schema": "http://json-schema.org/draft-04/schema#",
            "name": "P2",
            "type": "object",
            "required": [
                "name",
                "method",
                "channels",
                "columns"
            ],
            "properties": {
                "name": {
                    "type": "string",
                    "title": "Name",
                    "description": "Predictor name",
                    "minLength": 2
                },
                "file": {
                    "type": "string",
                    "title": "File",
                    "media": {
                        "binaryEncoding": "base64",
                        "type": "img/png"
                    },
                    "options": {
                        "grid_columns": 6,
                        "multiple": True,
                    }
                },
                "method": {
                    "type": "string",
                    "title": "Platform",
                    "enum": ["OpenSees","CSiBridge", "SAP2000"]
                },
                "algorithm": {
                    "type": "integer",
                    "title": "Algorithm",
                    "default": 100,
                    "minimum": 50,
                    "maximum": 500,
                    "options": {"dependencies": {"method": ["Nonlinear"]}}
                },
                "damping": {
                    "type": "number",
                    "title": "Damping",
                    "default": 0.02,
                    "options": {"dependencies": {"method": ["Response Spectrum"]}},
                    "description": "damping ratio"
                },
                "channels": {
                    "type": "array",
                    "format": "table",
                    "title": "Channels",
                    "uniqueItems": True,
                    "items": {
                        "title": "Channel",
                        "type": "object",
                        "required": ["node", "dof", 'sensor'],
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["output","input"],
                                "default": "output"
                            },
                            "sensor":  {"type": "integer", "description": "Number identifying sensor channel"},
                            "node":    {"type": "integer", "description": "Number identifying node"},
                            "dof":     {"type": "integer", "description": "Number identifying dof"},
                            "angle":   {"type": "number",  "description": "Number identifying angle"}
                        }
                    },
                    "default": [{"type": "output", "sensor": 1, "node": 1, "dof": 1}]
                },
                "columns": {
                    "type": "array",
                    "format": "table",
                    "title": "Columns",
                    "uniqueItems": True,
                    "items": {
                        "title": "Column",
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["output","input"],
                                "default": "output"
                            },
                            "id": {"type": "integer", "description": "Number identifying element"}
                        }
                    },
                    "default": [{"type": "output", "id": 1}],
                    "options": {"dependencies": {"method": ["SAP2000", "OpenSees"]}}
                }
            }
            }

        return {
            "title": "Structural Model",
            "options": {"disable_collaps": True},
            "schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "platform": {
                  "type": "string",
                  "title": "Platform",
                  "enum": ["OpenSees","CSiBridge"]
                },
                "model":    schemas.load("hwd_conf.schema.json"),
                "analysis": schemas.load("hwd_analysis.schema.json"),
            }
        }
    
    def render(self):
        import veux
        model = Job(self._csi).assemble().model

        outlines = collect_outlines(self._csi, model.frame_tags)
        artist = veux.render(model, canvas="gltf", vertical=3,
                                reference={"frame.surface", "frame.axes"},
                                model_config={"frame_outlines": outlines})
        return artist

    def getMetricList(self):
        return [
            "COLUMN_STRAIN_STATES",
            "PEAK_ACCEL",
            "PEAK_DRIFT",
            # "ACC_RESPONSE_HISTORY",
        ]


    def newPrediction(self, event, output_directory = None):
        """
        Create a new prediction run and return the run_id. If output_directory is None,
        the output directory will be created automatically.
        """
        inputs = {}
        for sensor in self.predictor.sensorassignment_set.all():
            if sensor.role == "input":
                inputs[sensor.id] = {"series": sensor.sensor.acceleration(event)}
        

        if output_directory is not None:
            # this case will eventually be deleted, its just for
            # debugging metric renderers.
            run_id = "0"
            self.runs[run_id] = {
                "run_output_directory": Path(output_directory)
            }

        else:
            # Calculate next output directory and
            # create directory if it doesn't exist
            out_dir = self.out_dir
            if not out_dir.is_dir():
                (out_dir/"0").mkdir(parents=True)

            latestDir = list(sorted((f for f in out_dir.iterdir() if f.is_dir()), key=lambda m: int(m.name)))[-1]
            run_id = int(latestDir.name)+1
            run_dir = out_dir/str(run_id)
            run_dir = run_dir.resolve()
            run_dir.mkdir(parents=True, exist_ok=False)

            # Copy files to run directory
            if False:
                event = event.event_file.path
                shutil.copyfile(event, run_dir/"event.zip")

            model_file = None
            if hasattr(self, "model_file") and self.model_file is not None:
                shutil.copyfile(self.model_file.resolve(),
                                run_dir/self.model_file.name)

                if self.model_file.suffix == ".zip":
                    with zipfile.ZipFile(self.model_file, 'r') as zip_ref:
                        zip_ref.extractall(run_dir)
                    model_file = (run_dir/"nonlinear.tcl").resolve()

                elif self.model_file.suffix == ".b2k":
                    pass

                elif self.model_file.suffix == ".tcl":
                    model_file = (run_dir/self.model_file.name).resolve()

            self.runs[run_id] = {
                "run_output_directory": run_dir,
                # "event_file_name": Path(event),
                "inputs": inputs,
                "model_file": model_file,
                **self.conf
            }

            with open(out_dir/str(run_id)/"conf.json", "w") as f:
                json.dump({k: str(v) for k,v in self.runs[run_id].items()}, f)

        return run_id


    def _load_config(self, run_id):
        run_dir =  self.out_dir/str(run_id)
        with open(run_dir/"conf.json","r") as f:
            self.runs[run_id] = json.load(f)

        self.model_file = Path(self.runs[run_id]["model_file"])


    def runPrediction(self, run_id, scale: float = None):
        if run_id not in self.runs:
            self._load_config(run_id)

        if False:
            event_file_path = os.path.relpath(self.runs[run_id]["event_file_name"],
                                            self.model_file.parents[0])

            output_directory = os.path.relpath(self.runs[run_id]["run_output_directory"],
                                            self.model_file.parents[0])

            event_file_path = self.runs[run_id]["event_file_name"]

        # Create model
        import opensees.openseespy as ops

        csi = self._csi 

        with new_cd(self.runs[run_id]["run_output_directory"]):

            model = ops.Model(ndm=3, ndf=6, echo_file=open("model.tcl", "w"))
            if csi is not None:
                asm = Job(csi).assemble(model=model)
                # model = create_model(csi, model=model)
                sections = collect_outlines(csi, model.frame_tags)
            else:
                asm = None
                sections = None
                model.eval(f"source {self.runs[run_id]['model_file']}")


            #
            # Run gravity analysis
            #
            model.eval("""
            wipeAnalysis
            test NormDispIncr 1.0e-8 10 0;
            algorithm Newton;
            integrator LoadControl 0.1;
            numberer Plain;
            constraints Transformation;
            system SparseGeneral;
            analysis Static;
            analyze 10;
            """)

            #
            # DAMPING
            #
            # model.eval(r"""
            # set nmodes 8; # Number of modes to analyze for modal analysis

            # # set wb [eigen -fullGenLapack $nmodes];
            # # puts "\tFundamental-Period After Gravity Analysis:"
            # # for {set iPd 1} {$iPd <= $nmodes} {incr iPd 1} {
            # #     set wwb [lindex $wb $iPd-1];
            # #     set Tb [expr 2*$pi/sqrt($wwb)];
            # #     puts "\tPeriod$iPd= $Tb"
            # # }
            # # write_modes $output_directory/modesPostG.yaml $nmodes
            # # remove recorders

            # set nmodes [tcl::mathfunc::max {*}$damping_modes $nmodes]
            # set lambdaN [eigen  -fullGenLapack $nmodes];

            # # set lambdaN [eigen $nmodes];
            # if {$damping_type == "rayleigh"} {
            #     set nEigenI [lindex $damping_modes 0];                  # first rayleigh damping mode
            #     set nEigenJ [lindex $damping_modes 1];                  # second rayleigh damping mode
            #     set iDamp   [lindex $damping_ratios 0];                 # first rayleigh damping ratio
            #     set jDamp   [lindex $damping_ratios 1];                 # second rayleigh damping ratio
            #     set lambdaI [lindex $lambdaN [expr $nEigenI-1]];
            #     set lambdaJ [lindex $lambdaN [expr $nEigenJ-1]];
            #     set omegaI [expr $lambdaI**0.5];
            #     set omegaJ [expr $lambdaJ**0.5];
            #     set TI [expr 2.0*$pi/$omegaI];
            #     set TJ [expr 2.0*$pi/$omegaJ];
            #     set alpha0 [expr 2.0*($iDamp/$omegaI-$jDamp/$omegaJ)/(1/$omegaI**2-1/$omegaJ**2)];
            #     set alpha1 [expr 2.0*$iDamp/$omegaI-$alpha0/$omegaI**2];
            #     puts "\tRayleigh damping parameters:"
            #     puts "\tmodes: $nEigenI, $nEigenJ ; ratios: $iDamp, $jDamp"
            #     puts "\tTI = $TI; TJ = $TJ"
            #     puts "\tlambdaI = $lambdaI; lambdaJ = $lambdaJ"
            #     puts "\tomegaI = $omegaI; omegaJ = $omegaJ"
            #     puts "\talpha0 = $alpha0; alpha1 = $alpha1"
            #     rayleigh $alpha0 0.0 0.0 $alpha1;

            # } elseif {$damping_type == "modal"} {
            #     # needs a bit of edit. currently assuming that the ratios are applied in order at the first modes. but should be applied at the specified damping_modes modes.
            #     set nratios [llength $damping_ratios]
            #     puts "\tModal damping parameters:"
            #     puts "\tratios of $damping_ratios at the first $nratios modes"
            #     for {set i 1} {$i <= [expr $nmodes - $nratios]} {incr i} {
            #         lappend damping_ratios 0
            #     }
            #     modalDamping {*}$damping_ratios
            # }
            # """)


            #
            # DYNAMIC RECORDERS
            #

            ## COLUMN SECTION DEFORMATIONS AT TOP AND BOTTOM FOR STRAIN-BASED DAMAGE STATES
            if False:
                column_strains = tuple(k["key"] for k in self.runs[run_id]["columns"] if k["strain"])
                if len(column_strains) > 0:
                    model.recorder("Element",  "section", 1, "deformation", xml="eleDef1.txt", ele=column_strains) # section 1 deformation]
                    model.recorder("Element",  "section", 4, "deformation", xml="eleDef4.txt", ele=column_strains) # section 4 deformation]

            #
            # Run dynamic analysis
            #

            # RESPONSE HISTORY RECORDERS
            if False:
                model.recorder("Node", "accel", xml="model/AA_all.txt", timeSeries=(1, 2), dof=(1, 2))
                model.recorder("Node", "accel", xml="model/RD_all.txt", dof=(1, 2))

                column_nodes = tuple(k["node"] for k in self.runs[run_id]["bents"] if k["record"])
                model.recorder("Node", "accel", file="TopColAccel_X_txt.txt", timeSeries=1 , node=column_nodes, dof=1)
                model.recorder("Node", "accel", file="TopColAccel_Y_txt.txt", timeSeries=2 , node=column_nodes, dof=2)
                model.recorder("Node", "disp",  file="TopColDrift_X_txt.txt", node=column_nodes, dof=1)
                model.recorder("Node", "disp",  file="TopColDrift_Y_txt.txt", node=column_nodes, dof=2)

            metrics = [
                PeakDrift((31, 81))
            ]

            for metric in metrics:
                metric.record(asm)


            nt = 500
            dt = 0.02
            _create_excitation(model, self.predictor, self.runs[run_id]["inputs"], dt)
            
            model.eval(f"print -json -file model.json")

            model.eval(f"""
            wipeAnalysis
            set NewmarkGamma    0.50;
            set NewmarkBeta     0.25;
            constraints Transformation;
            numberer    RCM;
            test        EnergyIncr 1.0e-6 50 0;
            system      Umfpack;
            integrator  Newmark $NewmarkGamma $NewmarkBeta;
            algorithm   Newton;
            analysis    Transient;
            """)

            import veux
            artist = veux.create_artist(model, vertical=3, model_config={
                    "frame_outlines": sections
            })
            _analyze_and_render(model, artist, nt, dt)

            artist.save("motion.glb")

            model.wipe()


    def getMetricData(self, run_id:int, type:str)->dict:
        import orjson
        def _clean_json(d):
            return orjson.loads(orjson.dumps(d,option=orjson.OPT_SERIALIZE_NUMPY))

        if run_id not in self.runs:
            self._load_config(run_id)

        run_data = self.runs.get(run_id, None)
        config = run_data

        if run_data is not None:
            output_dir = Path(run_data["run_output_directory"])
        else:
            output_dir = self.out_dir/str(run_id)

        model = read_model(output_dir/"model.json")

        # if type == "COLUMN_STRAIN_STATES":
        #     return _clean_json(column_strain_state_metric(model, output_dir, config))

#         if type == "PEAK_ACCEL":
#             return _clean_json(peak_acceleration_metric(output_dir, config))

#         elif type == "PEAK_DRIFT":
#             return _clean_json(peak_drift_metric(model, output_dir, config))

#         elif type == "ACC_RESPONSE_HISTORY":
#             # config = CONFIG
# #           return accel_response_history_plot(output_dir, config)
#             return {}
        return {}

    #
    # Viewing methods
    #

    @property
    def _csi(self):
        if not hasattr(self, "_csi_data") or self._csi_data is None:
            # 1) Parse the CSI file
            try:
                csi_file = self.predictor.config_file
                self._csi_data = load_csi((str(line.decode()).replace("\r\n","\n") for line in csi_file.readlines()))

            except Exception as e:
                import sys
                print(f"Error loading CSiBridge file: {e}", file=sys.stderr)
                self._csi_data = {}

        return self._csi_data


    def structural_section(self, name):
        if (s:= create_section(self._csi, name)) is not None:
            model = s._create_model(mesh_size=0.1)
            if model is None:
                return [], None
            cmm = model.cmm()
            cnn = model.cnn()
            cnm = model.cnm()
            properties = [
                {
                    "name": "Elastic", "data": [
                        {"name": "A",   "value": float(cnn[0,0])},
                        {"name": "Iyy", "value": float(cmm[1,1])},
                        {"name": "Izz", "value": float(cmm[2,2])},
                    ],
                },
                {
                    "name": "Ultimate", "data": [
                        # {"name": "A",   "value": float(cnn[0,0])},
                        # {"name": "Iyy", "value": float(cmm[1,1])},
                        # {"name": "Izz", "value": float(cmm[2,2])},
                    ]
                }
            ]
            return properties, model


    def structural_sections(self):
        yield from iter_sections(self._csi)


    def structural_members(self):

        for item in self._csi.get("BRIDGE BENT DEFINITIONS 2 - COLUMN DATA",[]):
            if "ColNum" in item and "Section" in item:
                yield {
                    "name": item["ColNum"],
                    "type": "Column",
                    # "section": item["Section"],
                }

        for item in self._csi.get("BRIDGE OBJECT DEFINITIONS 03 - SPANS 1 - GENERAL", []):
            if "SpanName" in item and "BridgeSect" in item:
                yield {
                    "name": item["SpanName"],
                    "type": "Span",
                    # "section": None,
                }


# import subprocess 
# class Event: pass 

# class PredictorType1(Runner):
#     @property
#     def platform(self):
#         return self.conf.get("platform", "")

#     @classmethod
#     def create(cls, asset, request):
#         from irie.apps.prediction.models import PredictorModel
#         predictor = PredictorModel()
#         data = json.loads(request.data.get("json"))
#         predictor.entry_point = [
#             sys.executable, "-m", "opensees"
#         ]
#         data["metrics"] = []

#         predictor.name = data.pop("name")
#         predictor.config = data
#         predictor.asset = asset
#         predictor.protocol = "IRIE_PREDICTOR_T1"
#         predictor.active = False
#         return predictor


#     @classproperty
#     def schema(cls):
#         from irie.apps.prediction.runners.opensees import schemas
#         return {
#             "title": "Structural Model",
#             "options": {"disable_collaps": True},
#             "schema": "http://json-schema.org/draft-04/schema#",
#             "type": "object",
#             "properties": {
#                 "platform": {
#                   "type": "string",
#                   "title": "Platform",
#                   "enum": ["OpenSees","CSiBridge"]
#                 },
#                 "model":    schemas.load("hwd_conf.schema.json"),
#                 "analysis": schemas.load("hwd_analysis.schema.json"),
#             }
#         }

#     def newPrediction(self, event: Event) -> RunID:
#         self.event = event
#         event_file = Path(event.event_file.path).resolve()
#         command = [*self.entry_point, "new", event_file]
#         run_id = subprocess.check_output(command).decode().strip()
#         return RunID(int(run_id))

#     def runPrediction(self, run_id: RunID):
#         command = [*self.entry_point, "run", str(run_id)]

#         if "scale" in self.event.upload_data:
#             command.extend(["--scale", str(float(self.event.upload_data["scale"]))])
#         print(":: Running ", command, file=sys.stderr)
#         subprocess.check_output(command)

#         print(f":: Model {self.name} returned", file=sys.stderr)
#         return

#     def getMetricData(self, run, metric):
#         try:
#             return json.loads(subprocess.check_output([*self.entry_point, "get", str(run), metric]).decode())
#         except json.decoder.JSONDecodeError:
#             return {}
