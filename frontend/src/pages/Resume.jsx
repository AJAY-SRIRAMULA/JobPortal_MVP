import {useEffect,useState} from 'react';
import api from '../services/api';

const empty={summary:'',education:'B.Tech / Degree',skills:'',projects:'',experience:'',certifications:''};

export default function Resume(){
  const [r,setR]=useState([]),[d,setD]=useState({name:'My Resume',data:empty}),[saved,setSaved]=useState(false),[file,setFile]=useState(null),[uploading,setUploading]=useState(false),[uploadMsg,setUploadMsg]=useState('');
  const load=()=>api.get('/resumes/').then(x=>setR(x.data));
  useEffect(()=>{load()},[]);
  const save=async()=>{try{await api.post('/resumes/',d);setSaved(true);load()}catch(e){setUploadMsg(e.response?.data?.detail||'Could not save resume')}};
  const upload=async()=>{
    if(!file)return;
    setUploading(true);setUploadMsg('');
    try{
      const fd=new FormData();
      fd.append('name',file.name.replace(/\.[^/.]+$/,''));
      fd.append('file',file);
      const res=await api.post('/resumes/upload/',fd,{headers:{'Content-Type':'multipart/form-data'}});
      setUploadMsg(`✓ ${res.data.file_name} uploaded successfully`);setFile(null);load();
    }catch(e){setUploadMsg(e.response?.data?.detail||'Resume upload failed')}finally{setUploading(false)}
  };
  return <div className="container py-4 py-lg-5">
    <div className="page-hero-row"><div><div className="eyebrow">SMART RESUME BUILDER</div><h1>Build once. Tailor for every role.</h1><p className="text-secondary">Create an ATS-friendly version or upload an existing resume directly from File Explorer.</p></div><button className="btn btn-dark" onClick={()=>window.print()}>Print / Save PDF</button></div>
    <div className="page-card mb-4 resume-upload-card">
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-3"><div><div className="eyebrow">UPLOAD FROM FILE EXPLORER</div><h4 className="mb-1">Already have a resume?</h4><p className="text-secondary mb-0">PDF, DOC and DOCX files are supported. Your selected file is stored with your candidate profile.</p></div><label className="upload-box resume-file-picker"><span>↑</span><b>{file?file.name:'Choose resume file'}</b><small>Click to browse your computer</small><input type="file" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={e=>setFile(e.target.files?.[0]||null)}/></label></div>
      <div className="d-flex flex-wrap align-items-center gap-2 mt-3"><button className="btn btn-primary" disabled={!file||uploading} onClick={upload}>{uploading?'Uploading…':'Upload resume'}</button>{uploadMsg&&<span className="small text-secondary">{uploadMsg}</span>}</div>
    </div>
    <div className="row g-4"><div className="col-lg-7"><div className="page-card"><label>Resume version name</label><input className="form-control mb-3" value={d.name} onChange={e=>setD({...d,name:e.target.value})}/>{Object.keys(d.data).map(k=><div key={k} className="mb-3"><label>{k.replace(/^\w/,c=>c.toUpperCase())}</label><textarea className="form-control" rows={k==='projects'||k==='experience'?4:2} value={d.data[k]} onChange={e=>setD({...d,data:{...d.data,[k]:e.target.value}})} placeholder={`Add your ${k}`}/></div>)}<button className="btn btn-primary" onClick={save}>Save resume version</button>{saved&&<span className="text-success ms-3">✓ Saved</span>}</div><div className="page-card mt-4"><div className="eyebrow">SAVED VERSIONS & UPLOADS</div>{r.length?r.map(x=><div className="saved-resume" key={x.id}><div><b>{x.name}</b>{x.data?.file_name&&<div className="small text-secondary">Uploaded file · {x.data.file_name}</div>}</div><span>{new Date(x.updated_at).toLocaleDateString()}</span></div>):<p className="text-secondary mb-0">No saved versions yet.</p>}</div></div><div className="col-lg-5"><div className="resume-preview resume-paper"><div className="eyebrow">LIVE PREVIEW</div><h2>{d.name}</h2>{Object.entries(d.data).map(([k,v])=><section key={k}><h6>{k.toUpperCase()}</h6><p>{v||'Add content here.'}</p></section>)}</div></div></div>
  </div>
}
