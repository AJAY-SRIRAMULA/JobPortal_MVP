import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth();

  if (!user) {
    return (
      <Navigate
        to={roles?.includes('admin') ? '/login' : roles?.includes('recruiter') ? '/recruiter-login' : '/candidate-login'}
        replace
      />
    );
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to={user.role === 'recruiter' ? '/recruiter' : '/dashboard'} replace />;
  }

  return children;
}
