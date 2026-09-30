import {BrowserRouter,Routes,Route} from 'react-router-dom';
import Layout from './components/Layout'; import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing'; import {Login,Register} from './pages/Auth'; import Jobs from './pages/Jobs'; import JobDetails from './pages/JobDetails';
import Dashboard from './pages/Dashboard'; import Recruiter from './pages/Recruiter'; import Assessments from './pages/Assessments'; import Resume from './pages/Resume';
import Refunds from './pages/Refunds'; import Internships from './pages/Internships'; import NotFound from './pages/NotFound'; import AI from './pages/AI'; import Admin from './pages/Admin'; import Interviews from './pages/Interviews';
import Companies from './pages/Companies'; import SavedJobs from './pages/SavedJobs'; import Profile from './pages/Profile'; import Messages from './pages/Messages';
export default function App(){return <BrowserRouter><Layout><Routes>
<Route path="/" element={<Landing/>}/><Route path="/login" element={<Login/>}/><Route path="/candidate-login" element={<Login role="candidate"/>}/><Route path="/recruiter-login" element={<Login role="recruiter"/>}/><Route path="/register" element={<Register/>}/>
<Route path="/jobs" element={<Jobs/>}/><Route path="/jobs/:id" element={<JobDetails/>}/><Route path="/companies" element={<Companies/>}/><Route path="/saved-jobs" element={<ProtectedRoute roles={['candidate']}><SavedJobs/></ProtectedRoute>}/><Route path="/internships" element={<Internships/>}/>
<Route path="/dashboard" element={<ProtectedRoute><Dashboard/></ProtectedRoute>}/><Route path="/profile" element={<ProtectedRoute roles={['candidate']}><Profile/></ProtectedRoute>}/>
<Route path="/messages" element={<ProtectedRoute><Messages/></ProtectedRoute>}/><Route path="/assessments" element={<ProtectedRoute roles={['candidate']}><Assessments/></ProtectedRoute>}/>
<Route path="/resume" element={<ProtectedRoute roles={['candidate']}><Resume/></ProtectedRoute>}/><Route path="/refunds" element={<ProtectedRoute roles={['candidate','admin']}><Refunds/></ProtectedRoute>}/>
<Route path="/recruiter" element={<ProtectedRoute roles={['recruiter','admin']}><Recruiter/></ProtectedRoute>}/><Route path="/interviews" element={<ProtectedRoute><Interviews/></ProtectedRoute>}/>
<Route path="/ai" element={<ProtectedRoute roles={['candidate']}><AI/></ProtectedRoute>}/><Route path="/admin" element={<ProtectedRoute roles={['admin']}><Admin/></ProtectedRoute>}/>
<Route path="*" element={<NotFound/>}/></Routes></Layout></BrowserRouter>}