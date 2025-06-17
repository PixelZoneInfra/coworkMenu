// menu logic
const params = new URLSearchParams(window.location.search);
const desk = params.get('desk') || '?';
document.getElementById('deskNum').textContent = desk;

const LIMIT = 2;
let used = 0;

document.querySelectorAll('.category-header').forEach(h => {
  h.onclick = () => h.nextElementSibling.classList.toggle('visible');
});

document.querySelectorAll('.item').forEach(item => {
  const dec = item.querySelector('.dec');
  const inc = item.querySelector('.inc');
  const input = item.querySelector('.qty');
  [dec, inc].forEach(btn => btn.onclick = () => {
    let v = parseInt(input.value) || 0;
    v = btn.classList.contains('inc') ? v+1 : v-1;
    if (v<0) v=0; if (v>20) v=20;
    input.value = v;
    input.parentElement.classList.toggle('active', v>0);
  });
  input.onfocus = () => input.parentElement.classList.add('active');
  input.onblur  = () => {
    if (parseInt(input.value)===0) input.parentElement.classList.remove('active');
  };
});

document.getElementById('clearAll').onclick = () => {
  document.querySelectorAll('.qty').forEach(i => {
    i.value=0; i.parentElement.classList.remove('active');
  });
};

document.getElementById('orderBtn').onclick = () => {
  const entries = [];
  document.querySelectorAll('.item').forEach(it => {
    const qty = parseInt(it.querySelector('.qty').value)||0;
    if (qty>0) {
      const name = it.querySelector('.item-name').textContent;
      entries.push({ name, qty });
    }
  });
  if (entries.length===0) {
    alert('Wybierz przynajmniej jedną pozycję.');
    return;
  }
  if (used >= LIMIT) {
    alert(`Limit zamówień (${LIMIT}) wyczerpany.`);
    return;
  }

  const list = document.getElementById('summaryList');
  list.innerHTML = entries.map(e => `<div>${e.qty}× ${e.name}</div>`).join('');
  document.getElementById('summaryModal').style.display = 'flex';

  document.getElementById('editBtn').onclick = () => {
    document.getElementById('summaryModal').style.display = 'none';
  };
  document.getElementById('confirmBtn').onclick = async () => {
    await fetch('/api/order', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        desk: parseInt(desk),
        items: entries.map(e=>`${e.qty}×${e.name}`).join(', ')
      })
    });
    used++;
    document.getElementById('limitInfo').textContent =
      `Pozostało zamówień: ${Math.max(0, LIMIT - used)}`;
    document.getElementById('summaryModal').style.display = 'none';
    document.getElementById('clearAll').click();
    alert('Zamówienie wysłane!');
  };
};

document.getElementById('limitInfo').textContent =
  `Pozostało zamówień: ${Math.max(0, LIMIT - used)}`;
