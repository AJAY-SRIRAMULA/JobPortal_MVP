export default function BarChart({data=[],labelKey='label',valueKey='value',suffix=''}) {
  const max=Math.max(...data.map(x=>Number(x[valueKey])||0),1);
  return <div className="bar-chart">
    {data.map((x,i)=><div className="bar-row" key={i}>
      <div className="bar-label"><span>{x[labelKey]}</span><strong>{x[valueKey]}{suffix}</strong></div>
      <div className="bar-track"><div className="bar-fill" style={{width:`${Math.max(4,(Number(x[valueKey])||0)/max*100)}%`}}/></div>
    </div>)}
  </div>
}