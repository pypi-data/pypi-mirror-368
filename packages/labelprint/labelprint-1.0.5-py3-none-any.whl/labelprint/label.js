//LabelPrint by Pecacheu; MIT License
lblData=async data => {
	let p=[],d,e;
	for(d in data) if(e=document.getElementById(d)) {
		if(e.tagName=='IMG') e.src=data[d], p.push(new Promise(r => {e.onload=r}));
		else e.innerHTML=data[d];
	}
	await Promise.all(p); window.onlabel&&(await onlabel(data));
	return 'lbl';
}