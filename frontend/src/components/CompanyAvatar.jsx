export default function CompanyAvatar({name='',size='md'}) {
 const initials=name.split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase()||'JP';
 return <div className={`company-avatar company-avatar-${size}`}>{initials}</div>
}