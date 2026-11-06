(()=>{const products=[
{id:'animals',cat:'animals',tag:'ЖИВОТНЫЕ',name:'Фигурки животных',desc:'Коты, собаки, драконы и другие модели для дома или подарка.',icon:'animal'},
{id:'characters',cat:'characters',tag:'ПЕРСОНАЖИ',name:'Персонажи и герои',desc:'Декоративные фигурки персонажей по выбранной или вашей модели.',icon:'character'},
{id:'auto',cat:'auto',tag:'АВТО / МОТО',name:'Авто и мото миниатюры',desc:'Миниатюры техники, деталей и тематические фигурки.',icon:'auto'},
{id:'miniatures',cat:'miniatures',tag:'МИНИАТЮРЫ',name:'Настольные миниатюры',desc:'Небольшие фигурки для коллекций, игр и диорам.',icon:'mini'},
{id:'busts',cat:'characters',tag:'БЮСТЫ',name:'Бюсты и статуэтки',desc:'Декоративные бюсты и интерьерные статуэтки разных размеров.',icon:'bust'},
{id:'custom',cat:'custom',tag:'ПО ФОТО',name:'Фигурка по вашей идее',desc:'Индивидуальный заказ по фото, эскизу или готовой 3D‑модели.',icon:'custom'},
{id:'keychains',cat:'miniatures',tag:'МИНИ',name:'Мини‑фигурки и брелоки',desc:'Компактные модели для подарков, наборов и сувениров.',icon:'keychain'},
{id:'decor',cat:'animals',tag:'ДЕКОР',name:'Декоративные фигурки',desc:'Интерьерные фигурки, статуэтки и необычный 3D‑декор.',icon:'decor'}
];
const icons={
animal:'<path d="M22 70c0-20 17-36 38-36s38 16 38 36v18H22V70Z"/><path d="M41 46 29 25l22 9M79 46l12-21-22 9"/>',
character:'<circle cx="60" cy="36" r="18"/><path d="M28 98V80c0-22 14-36 32-36s32 14 32 36v18H28Z"/>',
auto:'<path d="M18 72h84l-10-25H30L18 72Z"/><circle cx="37" cy="76" r="10"/><circle cx="83" cy="76" r="10"/><path d="M39 47 49 33h28l9 14"/>',
mini:'<path d="M35 88h50M42 88l6-20h24l6 20M52 68V46h16v22M48 46l12-16 12 16"/>',
bust:'<circle cx="60" cy="36" r="18"/><path d="M37 88c2-23 10-34 23-34s21 11 23 34H37ZM30 94h60"/>',
custom:'<rect x="28" y="25" width="64" height="70" rx="8"/><circle cx="60" cy="48" r="12"/><path d="M42 82c3-15 9-22 18-22s15 7 18 22"/>',
keychain:'<circle cx="45" cy="42" r="15"/><path d="M56 54l22 24M72 72l12-12 9 9-12 12"/>',
decor:'<path d="M36 90h48M43 90l5-18h24l5 18M52 72l-8-22 16-20 16 20-8 22"/>'
};
const grid=document.querySelector('#productGrid'),filters=[...document.querySelectorAll('[data-filter]')],cartOpen=document.querySelector('#cartOpen'),cartClose=document.querySelector('#cartClose'),drawer=document.querySelector('#cartDrawer'),backdrop=document.querySelector('#cartBackdrop'),list=document.querySelector('#cartList'),empty=document.querySelector('#cartEmpty'),count=document.querySelector('#cartCount'),send=document.querySelector('#sendOrder');
let cart=JSON.parse(localStorage.getItem('a4_3d_cart')||'[]');
function productCard(p){return '<article class="product-card" data-cat="'+p.cat+'"><div class="product-visual"><span class="product-tag">'+p.tag+'</span><svg viewBox="0 0 120 120">'+icons[p.icon]+'</svg></div><div class="product-body"><h3>'+p.name+'</h3><p>'+p.desc+'</p><div class="product-options"><label><span>РАЗМЕР</span><select class="size"><option>Мини</option><option selected>Средний</option><option>Большой</option></select></label><label><span>ЦВЕТ</span><select class="color"><option>Белый</option><option>Чёрный</option><option selected>Цветной</option><option>Другой</option></select></label></div><div class="product-bottom"><div class="product-price"><strong>По расчёту</strong><small>после выбора параметров</small></div><button class="add-cart" data-id="'+p.id+'">В корзину</button></div></div></article>'}
grid.innerHTML=products.map(productCard).join('');
filters.forEach(btn=>btn.addEventListener('click',()=>{filters.forEach(x=>x.classList.remove('active'));btn.classList.add('active');const f=btn.dataset.filter;document.querySelectorAll('.product-card').forEach(c=>c.hidden=f!=='all'&&c.dataset.cat!==f)}));
grid.addEventListener('click',e=>{const b=e.target.closest('.add-cart');if(!b)return;const card=b.closest('.product-card'),p=products.find(x=>x.id===b.dataset.id),size=card.querySelector('.size').value,color=card.querySelector('.color').value,existing=cart.find(x=>x.id===p.id&&x.size===size&&x.color===color);if(existing)existing.qty++;else cart.push({id:p.id,name:p.name,size,color,qty:1});save();openCart()});
function save(){localStorage.setItem('a4_3d_cart',JSON.stringify(cart));renderCart()}
function renderCart(){count.textContent=cart.reduce((s,x)=>s+x.qty,0);empty.hidden=cart.length>0;list.innerHTML=cart.map((x,i)=>'<div class="cart-item"><div class="cart-item__top"><div><h3>'+x.name+'</h3><p>'+x.size+' · '+x.color+'</p></div><button data-remove="'+i+'" aria-label="Удалить">×</button></div><div class="cart-item__qty"><button data-minus="'+i+'">−</button><strong>'+x.qty+'</strong><button data-plus="'+i+'">+</button></div></div>').join('');send.disabled=!cart.length}
list.addEventListener('click',e=>{const r=e.target.dataset.remove,m=e.target.dataset.minus,p=e.target.dataset.plus;if(r!==undefined){cart.splice(+r,1)}else if(m!==undefined){cart[+m].qty--;if(cart[+m].qty<=0)cart.splice(+m,1)}else if(p!==undefined){cart[+p].qty++}save()});
function openCart(){drawer.classList.add('open');drawer.setAttribute('aria-hidden','false');backdrop.hidden=false}
function closeCart(){drawer.classList.remove('open');drawer.setAttribute('aria-hidden','true');backdrop.hidden=true}
cartOpen.addEventListener('click',openCart);cartClose.addEventListener('click',closeCart);backdrop.addEventListener('click',closeCart);
send.addEventListener('click',()=>{if(!cart.length)return;const lines=cart.map((x,i)=>(i+1)+'. '+x.name+' — '+x.size+', '+x.color+', '+x.qty+' шт.');const body='Здравствуйте! Хочу заказать 3D‑фигурки:%0D%0A%0D%0A'+encodeURIComponent(lines.join('\n'))+'%0D%0A%0D%0AПрошу рассчитать стоимость.';location.href='mailto:a4-print@bk.ru?subject='+encodeURIComponent('Заказ 3D‑фигурок')+'&body='+body});
renderCart()})();