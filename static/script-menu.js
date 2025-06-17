(() => {
  const params = new URLSearchParams(location.search);
  const desk = parseInt(params.get('desk')) || 0;
  document.getElementById('deskNum').textContent = desk;

  const limitBar = { el: document.getElementById('limitBar'),
    used: document.getElementById('used'),
    limit: document.getElementById('limit'),
    timer: document.getElementById('timer')
  };
  const LIMIT_URL = `/api/limit/${desk}`;
  let resetSec = 0, timerId;

  // Pobierz stan limitu
  async function fetchLimit() {
    const res = await fetch(LIMIT_URL); const js=await res.json();
    limitBar.used.textContent = js.used;
    limitBar.limit.textContent = js.limit;
    resetSec = js.remaining;
    limitBar.timer.textContent = resetSec;
    if (timerId) clearInterval(timerId);
    timerId = setInterval(() => {
      resetSec--; 
      if (resetSec<0) fetchLimit();
      else limitBar.timer.textContent = resetSec;
    },1000);
  }

  // Akordeon
  document.querySelectorAll('.category-header').forEach(h=>
    h.onclick=()=> h.nextElementSibling.classList.toggle('visible')
  );

  // Qty
  document.querySelectorAll('.item').forEach(it => {
    const dec=it.querySelector('.dec'),
          inc=it.querySelector('.inc'),
          inp=it.querySelector('.qty');
    dec.onclick = ()=> { inp.stepDown(); updateSummary(); };
    inc.onclick = ()=> { inp.stepUp(); updateSummary(); };
    inp.oninput = updateSummary;
  });

  document.getElementById('clearAll').onclick = () => {
    document.querySelectorAll('.qty').forEach(i=>i.value=0);
    updateSummary();
  };

  const summary = {
    el: document.getElementById('summary'),
    list: document.getElementById('summaryList'),
    sum:  document.getElementById('summarySum'),
    confirm: document.getElementById('confirmBtn'),
    edit: document.getElementById('editBtn')
  };

  let currentCart=[];

  function updateSummary() {
    currentCart = [];
    let total=0;
    document.querySelectorAll('.item').forEach(it=>{
      const q=+it.querySelector('.qty').value;
      if(q>0){
        const name=it.dataset.name;
        const price=+it.dataset.price;
        currentCart.push({name,qty:q,price});
        total += q*price;
      }
    });
    if(currentCart.length){
      summary.list.innerHTML = currentCart.map(c=>
        `<div>${c.qty}× ${c.name} – ${(c.qty*c.price).toFixed(2)} PLN</div>`
      ).join('');
      summary.sum.textContent = total.toFixed(2);
      summary.el.classList.remove('hidden');
    } else {
      summary.el.classList.add('hidden');
    }
  }

  summary.confirm.onclick = async () => {
    if(!currentCart.length) return;
    // Wyślij
    await fetch('/api/order', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        desk, items: currentCart.map(c=>`${c.qty}×${c.name}`)
      })
    });
    alert('Zamówienie przyjęte');
    currentCart=[]; updateSummary(); fetchLimit();
  };
  summary.edit.onclick = () => summary.el.classList.add('hidden');

  // Init
  fetchLimit();
  document.getElementById('orderBtn').onclick = ()=>{};// już robione w summary
})();
