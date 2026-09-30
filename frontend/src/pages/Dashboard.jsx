import {useEffect,useMemo,useRef,useState} from 'react';
import {Link} from 'react-router-dom';
import api from '../services/api';
import BarChart from '../components/BarChart';

function CompanyAvatar({name='Company'}){const initials=name.split(' ').filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase();return <div className="app-avatar">{initials||'C'}</div>}

const startupHubs=[
  {name:'HITEC City',lat:17.4435,lng:78.3772,description:'Major technology and startup cluster'},
  {name:'Madhapur',lat:17.4483,lng:78.3915,description:'Technology, product and services companies'},
  {name:'Kondapur',lat:17.4580,lng:78.3658,description:'Growing product and engineering hub'},
  {name:'Gachibowli',lat:17.4401,lng:78.3489,description:'IT, fintech and enterprise technology'},
  {name:'Financial District',lat:17.4239,lng:78.3430,description:'Large technology and business campus area'},
  {name:'Raidurg',lat:17.4146,lng:78.3433,description:'Corporate and technology district'},
];

const hubCoords={
  'HITEC City':[17.4435,78.3772],'Madhapur':[17.4483,78.3915],'Kondapur':[17.4580,78.3658],
  'Gachibowli':[17.4401,78.3489],'Financial District':[17.4239,78.3430],'Raidurg':[17.4146,78.3433],
  'Hyderabad':[17.3850,78.4867]
};

export default function Dashboard(){
 const [dashboard,setDashboard]=useState({}),[apps,setApps]=useState([]),[me,setMe]=useState(null),[nearbyJobs,setNearbyJobs]=useState([]);
 const mapRef=useRef(null),leafletMapRef=useRef(null);
 const load=async()=>{try{const [d,a,m,j]=await Promise.all([api.get('/dashboard/'),api.get('/applications/'),api.get('/me/'),api.get('/jobs/?location=Hyderabad')]);setDashboard(d.data||{});setApps(a.data||[]);setMe(m.data||null);setNearbyJobs((j.data||[]).slice(0,8));}catch(e){console.error('Unable to load candidate dashboard',e)}};
 useEffect(()=>{load()},[]);
 const gaps=useMemo(()=>{const counts={};apps.forEach(a=>(a.missing_skills||[]).forEach(s=>counts[s]=(counts[s]||0)+1));return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([label,value])=>({label,value}))},[apps]);
 const stageCount=[['Applied',apps.length],['Shortlisted',apps.filter(a=>a.status==='SHORTLISTED').length],['Interview',apps.filter(a=>a.interview).length],['Selected',apps.filter(a=>a.status==='SELECTED').length]];
 const verifiedSkills=me?.profile?.skills?.filter(s=>s.status==='VERIFIED').length||0,totalSkills=me?.profile?.skills?.length||0;

 useEffect(()=>{
   if(!mapRef.current || !window.L) return;
   if(leafletMapRef.current){leafletMapRef.current.remove();leafletMapRef.current=null;}
   const L=window.L;
   const map=L.map(mapRef.current,{scrollWheelZoom:true,zoomControl:true}).setView([17.4401,78.3650],12.5);
   leafletMapRef.current=map;
   L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
   const hubIcon=L.divIcon({className:'jobportal-hub-icon',html:'<span>✦</span>',iconSize:[34,34],iconAnchor:[17,17],popupAnchor:[0,-18]});
   const jobIcon=L.divIcon({className:'jobportal-job-icon',html:'<span>•</span>',iconSize:[24,24],iconAnchor:[12,12],popupAnchor:[0,-12]});
   startupHubs.forEach(h=>L.marker([h.lat,h.lng],{icon:hubIcon}).addTo(map).bindPopup(`<strong>${h.name}</strong><br/><span>${h.description}</span><br/><small>Public startup/technology hub · approximate area</small>`));
   nearbyJobs.forEach((job,index)=>{
     const loc=String(job.location||'Hyderabad');
     const match=Object.keys(hubCoords).find(k=>loc.toLowerCase().includes(k.toLowerCase()));
     const base=hubCoords[match||'Hyderabad'];
     const lat=base[0]+((index%3)-1)*0.006;
     const lng=base[1]+((index%4)-1.5)*0.006;
     L.marker([lat,lng],{icon:jobIcon}).addTo(map).bindPopup(`<strong>${String(job.title||'Job opening').replace(/</g,'&lt;')}</strong><br/><span>${String(job.company?.name||'Company').replace(/</g,'&lt;')} · ${String(job.location||'Hyderabad').replace(/</g,'&lt;')}</span><br/><small>${String(job.salary||'Salary available').replace(/</g,'&lt;')}</small><br/><a href="/jobs/${job.id}">View opening →</a>`);
   });
   const bounds=L.latLngBounds(startupHubs.map(h=>[h.lat,h.lng]));
   map.fitBounds(bounds,{padding:[24,24]});
   setTimeout(()=>map.invalidateSize(),100);
   return ()=>{if(leafletMapRef.current){leafletMapRef.current.remove();leafletMapRef.current=null;}};
 },[nearbyJobs]);

 return <div className="container py-4 py-lg-5">
  <div className="dashboard-hero candidate-dashboard-header"><div className="dashboard-heading"><div className="eyebrow">CANDIDATE COMMAND CENTER</div><h1>Good to see you, {me?.first_name||'there'}.</h1><p>One view for your applications, skill growth, interviews and refunds.</p></div><div className="quick-actions"><Link to="/jobs" className="btn btn-primary">Find jobs</Link><Link to="/resume" className="btn btn-light">Update resume</Link></div></div>
  <div className="row g-3 mb-4">{[['Applications',dashboard.applications,'↗'],['Priority',dashboard.priority_applications,'★'],['Shortlisted',dashboard.shortlisted,'✓'],['Interviews',dashboard.interviews,'◷'],['Selected',dashboard.selected,'◆'],['Avg match',`${dashboard.average_match||0}%`,'◎']].map(([label,value,icon])=><div className="col-6 col-md-4 col-xl-2" key={label}><div className="stat-card-modern"><span>{icon}</span><small>{label}</small><strong>{value??0}</strong></div></div>)}</div>
  <div className="row g-4"><div className="col-lg-8"><div className="page-card"><div className="card-head"><div><div className="eyebrow">APPLICATION TRACKER</div><h3>Your applications</h3></div><Link to="/jobs">+ Apply</Link></div>{apps.length?apps.map(a=><div className="application-row" key={a.id}><div className="app-logo"><CompanyAvatar name={a.job?.company?.name||'Company'}/></div><div className="flex-grow-1"><div className="d-flex justify-content-between gap-2"><div><b>{a.job?.title||'Job application'}</b><div className="small text-secondary">{a.job?.company?.name||'Company'} · {a.job?.location||'Location not specified'}</div></div><span className={`status-chip status-${String(a.status||'APPLIED').toLowerCase()}`}>{String(a.status||'APPLIED').replace(/_/g,' ')}</span></div><div className="match-line"><span>Match {a.match_percent||0}%</span><div className="meter"><span style={{width:`${Math.min(100,Math.max(0,a.match_percent||0))}%`}}/></div></div><div className="stage-mini"><span className={a.status==='APPLIED'?'on':''}>Applied</span><span className={a.interview?'on':''}>Interview</span><span className={['SELECTED','REJECTED'].includes(a.status)?'on':''}>Outcome</span></div></div></div>):<div className="empty">No applications yet. Your next role is waiting in the job marketplace.</div>}</div></div>
   <div className="col-lg-4"><div className="page-card mb-4"><div className="card-head"><h3>Skill gap signals</h3><Link to="/jobs">Improve</Link></div>{gaps.length?<BarChart data={gaps}/>:<p className="text-secondary mb-0">Apply to roles to generate a role-specific skill gap.</p>}<div className="passport-mini mt-4"><span>Verified Skill Passport</span><strong>{verifiedSkills} verified</strong><small>{totalSkills} total declared skills</small></div></div><div className="page-card"><div className="card-head"><h3>Application funnel</h3></div><BarChart data={stageCount.map(([label,value])=>({label,value}))}/></div></div></div>
  <div className="page-card nearby-startups-card mt-4"><div className="section-heading compact"><div><div className="eyebrow">NEARBY OPPORTUNITIES</div><h2>Interactive startup map & nearby openings</h2><p className="text-secondary mb-0">Zoom, pan and click a hub or job marker. Locations are approximate public startup clusters.</p></div><Link to="/jobs" className="text-link">View all openings →</Link></div><div className="map-toolbar"><span>✦ Startup hub</span><span>• Job opening</span><span className="map-note">Map data © OpenStreetMap contributors</span></div><div className="row g-4 align-items-stretch"><div className="col-lg-7"><div ref={mapRef} className="startup-map interactive-map" aria-label="Interactive Hyderabad startup and job map"/></div><div className="col-lg-5"><div className="nearby-job-list">{nearbyJobs.length?nearbyJobs.map(j=><Link to={`/jobs/${j.id}`} className="nearby-job" key={j.id}><div><span>{j.industry||'Opportunity'}</span><h5>{j.title}</h5><p>{j.company?.name||'Company'} · {j.location}</p></div><strong>{j.salary}</strong></Link>):<div className="empty">No nearby openings available yet.</div>}</div></div></div></div>
  <div className="row g-4 mt-1"><div className="col-md-4"><div className="feature-card compact"><span className="feature-icon">✦</span><h5>AI Career Assistant</h5><p>Ask about skills, resume or interview prep.</p><Link to="/ai">Open assistant →</Link></div></div><div className="col-md-4"><div className="feature-card compact"><span className="feature-icon">✓</span><h5>Skill assessments</h5><p>Build evidence behind your skill passport.</p><Link to="/assessments">Take assessment →</Link></div></div><div className="col-md-4"><div className="feature-card compact"><span className="feature-icon">↺</span><h5>Escrow & refunds</h5><p>See every fee and eligibility state.</p><Link to="/refunds">Track refunds →</Link></div></div></div>
 </div>
}
