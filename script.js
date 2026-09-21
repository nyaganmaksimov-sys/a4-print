(()=>{const b=document.querySelector('.menu-button'),n=document.querySelector('#mainNav');b?.addEventListener('click',()=>{const o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!o));n.classList.toggle('open',!o)});n?.addEventListener('click',e=>{if(e.target.closest('a')){n.classList.remove('open');b?.setAttribute('aria-expanded','false')}});

const input=document.querySelector('#serviceSearch'),heroInput=document.querySelector('#heroSearch'),clear=document.querySelector('#clearSearch'),groups=[...document.querySelectorAll('.catalog-group')],empty=document.querySelector('#catalogEmpty');
const norm=s=>s.toLowerCase().replace(/ё/g,'е').replace(/[^a-zа-я0-9]+/gi,' ').trim();
function render(){
  const q=norm(input?.value||'');let visible=0;
  groups.forEach(g=>{const hay=norm((g.dataset.search||'')+' '+g.textContent),ok=!q||q.split(' ').every(t=>hay.includes(t));g.hidden=!ok;if(ok)visible++});
  if(clear)clear.hidden=!q;
  if(empty)empty.hidden=visible!==0;
}
input?.addEventListener('input',()=>{if(heroInput&&heroInput.value!==input.value)heroInput.value=input.value;render()});
heroInput?.addEventListener('input',()=>{if(input){input.value=heroInput.value;render()}});
heroInput?.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();document.querySelector('#catalog')?.scrollIntoView({behavior:'smooth',block:'start'});setTimeout(()=>input?.focus(),450)}});
clear?.addEventListener('click',()=>{if(input)input.value='';if(heroInput)heroInput.value='';input?.focus();render()});
render();
const y=document.querySelector('#year');if(y)y.textContent=new Date().getFullYear()})();