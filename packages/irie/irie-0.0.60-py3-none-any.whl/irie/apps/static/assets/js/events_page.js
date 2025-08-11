'use strict';
const e = React.createElement;

const HiddenRow = React.forwardRef((props, ref)=>(
  <tr className="collapse hide-table-padding" 
   key={"collapse-"+props.id} 
   id={"collapse-"+props.id}
   ref={ref}>
    <td></td>
    <td colSpan="3">
      <p><code>station_name</code>: {props.motion_components["station_name"]}</p>
      <p><code>peak_accel</code>:   {props.motion_components["peak_accel"]}</p>
      <p><code>event_date</code>:   {props.motion_components["event_date"]}</p>
      <p><code>record_identifier</code>:   {props.motion_components["record_identifier"]}</p>
    </td>
  </tr>
));

class QuakeEventRow extends React.Component {
  state = {expanded: false};

  constructor(props) {
    super(props);
    Object.assign(this, {...props});
    this.detail_ref = React.createRef();
    this.handleClick = this.handleClick.bind(this);
    this.toggleExpand = this.toggleExpand.bind(this);
  }

  toggleExpand(){
    console.log('ref: ', this.detail_ref);
    if (!this.state.expanded){
      this.setState({expanded: true});
      this.detail_ref.current && this.detail_ref.current.classList.add("show");
    } else {
      this.setState({expanded: false});
      this.detail_ref.current && this.detail_ref.current.classList.remove("show");
    }
  }

  handleClick() {
    this.toggleExpand();
  }

  render() {
    return [
      <tr key={"prow" + this.id} 
          className="accordion-toggle collapsed"
          data-toggle="collapse" 
          data-target={"#collapse-"+this.id}
          href={"#collapse-"+this.id}
      >
          <td>{this.id}</td>
          <td>{this.upload_date}</td>
          {/* <td>{this.item}</td> */}
          <td><code>{this.event_file.split("/").slice(-1)}</code></td>
          <td>
            <a className="btn btn-light" style={{marginLeft: "auto"}}
              onClick={()=>{this.handleClick()}}>Details</a>
          {/*
            <a className="btn btn-light" style={{marginLeft: "auto"}}
              onClick={(e)=>{editEvent(this)}}>Edit</a>{" "}
            <a className="btn btn-light" style={{marginLeft: "auto"}}
              onClick={(e)=>{deleteEvent(this.id)}}>Delete</a>
           */}
          </td>
        </tr>,

        <HiddenRow key={"hrow-"+this.id} ref={this.detail_ref} id={this.id} motion_components={this.motion_data} />
    ];
  }
}

function App() {
  const [list, setList] = React.useState([]);
  const [count, setCount] = React.useState(0);
  const [pages, setPages] = React.useState([]);
  const [page, setPage] = React.useState(0);
  const [showModal, setShowModal] = React.useState(false);
  const [showQuakeEventView, setShowQuakeEventView] = React.useState(false);
  const [modalDescription, setModalDescription] = React.useState("");
  const [itemId, setItemId] = React.useState(null);
  const [error, setError] = React.useState("");

  const [item, setItem] = React.useState("");
  const [quakeEventName, setQuakeEventName] = React.useState("");
  const [quakeEventFile, setQuakeEventFile] = React.useState();
  const [isFileSelected, setIsFileSelected] = React.useState(false);


  const success = (data) => {
    setList(data.data);
    setCount(data.count);
    const newPages = [];
    if (data.count > 10) {
      for (let i=0; i < Math.ceil(data.count / 10); i++) {
        newPages.push({
          name: (i+1).toString(),
          page: i,
        });
        console.log("page",i);
      }
      if (page > newPages.length-1) {
        setPage(page-1);
      }
    } else {
      setPage(0);
    }
    setPages(newPages);
  };

  const logout = async (e)=>{
    await localStorage.setName("salesToken",null);
    window.location = "/login";
  };

  const getData = ()=>{
    get_events_api(page, success, (text)=>{console.log("Error: ", text)});
  };

  const newEvent = ()=>{
    setModalDescription("New event");
    setItemId(null);
    setQuakeEventName("");
    setError("");
    setShowModal(true);
    const itemInput = document.getElementById("itemInput");
    setTimeout(()=>{itemInput && itemInput.focus()}, 1);
  };

  const editEvent = (data)=>{
    setModalDescription("New event");
    setItemId(data.id);
    setQuakeEventName(data.upload_data.name);
    setError("");
    setShowModal(true);
    const itemInput = document.getElementById("itemInput");
    setTimeout(()=>{itemInput && itemInput.focus()}, 1);
  };

  const saveEvent = (e)=>{
    e.preventDefault();
    setError("");
    console.log("saving new", item, price);
    if (item.length * price  === 0)
      setError("Please enter item name, price");
    else {
      if (itemId === null)
        post_event_api({item, price}, ()=>{getData();});
      else
        put_event_api(itemId, {item, price}, ()=>{getData();});
      setShowModal(false);
    }
  };

  const deleteEvent = (eventId)=>{
    Swal.fire({
      title: 'Are you sure?',
      text: "You will not be able to revert this.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it.'
    }).then((result) => {
      if (result.isConfirmed) {
        delete_event_api(eventId, ()=>{
          Swal.fire({
              title: 'Deleted!',
              text: "Your event has been deleted.",
              icon: 'success',
              timer: 1000,
          });
          getData();
        });
      }
    });
  };

  const viewQuakeEvent = (eventId)=>{
    setModalDescription("View event");
    setShowQuakeEventView(true);
    setShowModal(true);
    // const itemInput = document.getElementById("itemInput");
    // setTimeout(()=>{itemInput && itemInput.focus()}, 1);
  };

  const keyDownHandler = (e)=>{
    if (e.which === 27)
      setShowModal(false);
  };

  React.useEffect(()=>{
    getData();
  }, [page]);

  return (
    <div onKeyDown={keyDownHandler}>
      <div style={{background: "#00000060"}}
          className={"modal " + (showModal?" show d-block":" d-none")} tabIndex="-1" role="dialog">
        <div className="modal-dialog shadow">
          <form method="post">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{modalDescription}</h5>
              <button type="button" className="btn-close" onClick={()=>{setShowModal(false)}} aria-label="Close"></button>
            </div>
            <div className="modal-body">
              <label>Item name</label>
                <div className="form-group">
                  <input type="text" className="form-control" name="item" id="itemInput"
                         value={item} onChange={(e)=>{setQuakeEventName(e.target.value)}}
                         placeholder="Item name"/>
                </div>
                <label style={{marginTop: "1em"}}>Event file</label>
                <div className="form-group">
                  <input type="file" className="form-control"
                         onChange={(e)=>{setQuakeEventFile(e.target.files[0]); setIsFileSelected(true);}}
                         name="quakeEventFile" />
                  { isFileSelected ? (
                    <p>File selected</p>
                  ) : (
                    <p>Select file to upload</p>
                  )
                  }
                  <div>
                    <button className="btn-primary" onClick={(e)=>{}} >Upload</button>
                  </div>
                </div>
              <small className="form-text text-muted">{error}</small>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={()=>{setShowModal(false)}} data-bs-dismiss="modal">Close</button>
              <button type="submit" className="btn btn-primary" onClick={saveEvent}>Save changes</button>
            </div>
          </div>
          </form>
        </div>
      </div>

      <div style={{maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
                    padding: "1em"}} className="shadow">
        <div style={{display: "flex", flexDirection: "row"}}>
          <span>Event Uploader</span>
          <a className="btn btn-light" style={{marginLeft: "auto"}} onClick={logout}>Logout</a>
        </div>
      </div>
      <div style={{maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
                    padding: "1em"}} className="shadow">
        <div style={{display: "flex", flexDirection: "row", marginBottom: "5px"}}>
          {pages.length > 0 && <nav className="d-lg-flex justify-content-lg-end dataTables_paginate paging_simple_numbers">
            <ul className="pagination">
              <li className={"page-item " + (page === 0?"disabled":"")} onClick={(e)=>{
                    e.preventDefault();
                    setPage(Math.max(page-1,0));
              }}><a className="page-link" href="#" aria-label="Previous"><span
                  aria-hidden="true">«</span></a></li>
              {pages.map((el)=><li key={"page" + el.page} onClick={(e)=>{
                  setPage(el.page);
                }} className={"page-item "+(page===el.page?"active":"")}>
                <a className="page-link" href="#">
                  {el.name}
                </a></li>)}
              <li className={"page-item " + (page === pages.length-1?"disabled":"")} onClick={(e)=>{
                    setPage(Math.min(page+1,pages.length-1));
              }}><a className="page-link" href="#" aria-label="Next"><span
                  aria-hidden="true">»</span></a></li>
            </ul>
          </nav>}
          <a className="btn btn-light" style={{marginLeft: "auto"}}
             onClick={newEvent}
          >Upload Event</a>
        </div>
        <table key="myTable" className="table table-hover caption-top">
          <thead className="table-light">
          <tr>
            <th>id</th>
            <th>Upload Date</th>
            <th>Name</th>
            <th>Action</th>
          </tr>
          </thead>
          <tbody>
            { list.map((row,idx)=><QuakeEventRow key={"row-"+idx} {...row} />)}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const domContainer = document.querySelector('#reactAppContainer');
ReactDOM.render(
  e(App),
  domContainer
);

