import {createContext,useContext,useEffect,useState} from 'react'; 
import api from '../services/api';
const C=createContext(); 
export const useAuth=()=>useContext(C);
export function AuthProvider({children})
{const [user,setUser]=useState(null); 
    useEffect(()=>{if(localStorage.getItem('access'))api.get('/me/').then(r=>setUser(r.data)).catch(()=>localStorage.clear())},[]); 
    const login=async d=>{const r=await api.post('/auth/login/',d);localStorage.setItem('access',r.data.access);
        localStorage.setItem('refresh',r.data.refresh);setUser(r.data.user);
        return r.data}; const register=async d=>{const r=await api.post('/auth/register/',d);
            localStorage.setItem('access',r.data.access);
            localStorage.setItem('refresh',r.data.refresh);
            setUser(r.data.user);return r.data}; 
            const logout=()=>{localStorage.clear();setUser(null)}; 
            return <C.Provider value={{user,login,register,logout}}>{children}</C.Provider>}
