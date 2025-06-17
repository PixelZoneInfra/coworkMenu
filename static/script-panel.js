(() => {
  const A = document.getElementById('active'),
        D = document.getElementById('done'),
        toggle = document.getElementById('toggleAlarm');
  let prevActive=0, pulse=null, alarm=true;

  toggle.onclick = () => { alarm=false; stop(); };

  function randColor(){
    return `rgb(${[0,1,2].map(_=>Math.floor(Math.random()*256)).join(',')})`;
  }
  function start(){
    if(!alarm||pulse) return;
    pulse = setInterval(()=> document.body.style.backgroundColor=randColor(),1000);
  }
  function stop(){
    clearInterval(pulse); pulse=null;
    document.body.style.backgroundColor='white';
  }

  async function reload(){
    const res = await fetch('/api/orders'),
          js = await res.json();
    render(js.active, A, false);
    render(js.done, D, true);
    if(js.active.length > prevActive) alarm=true;
    prevActive = js.active.length;
    js.active.length && alarm ? start() : stop();
  }

  function render(arr, container, isDone){
    container.innerHTML = '';
    arr.forEach(o => {
      const div = document.createElement('div');
      div.className='order';
      div.innerHTML = `
        <div><strong>#${o.id}</strong> stolik ${o.desk}</div>
        <div>${o.items.split(',').map(i=>'<div>'+i+'</div>').join('')}</div>
      `;
      div.onclick = async ()=>{
        // PATCH toggle
        await fetch(`/api/order/${o.id}`, { method:'PATCH' });
        reload();
      };
      container.appendChild(div);
    });
  }

  reload();
  setInterval(reload,2000);
})();
