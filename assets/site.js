(function(){
'use strict';
const search=document.getElementById('eraSearch');
if(search){
 const cards=[...document.querySelectorAll('.era-card')];
 const buttons=[...document.querySelectorAll('.filter-btn')];
 let category='all';
 function normalize(s){return (s||'').toLocaleLowerCase('ko-KR').normalize('NFC').replace(/\s+/g,' ')}
 function render(){
  const q=normalize(search.value.trim());let n=0;
  for(const c of cards){
   const matchesText=!q||normalize(c.getAttribute('data-filter')).includes(q);
   const matchesCategory=category==='all'||c.getAttribute('data-category')===category;
   c.hidden=!(matchesText&&matchesCategory);
   if(!c.hidden)n++;
  }
  document.getElementById('resultCount').textContent=n;
  document.getElementById('noResults').hidden=!!n;
 }
 search.addEventListener('input',render);
 buttons.forEach(b=>b.addEventListener('click',()=>{
  category=b.dataset.category;
  buttons.forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});
  render();
 }));
 render();
}
const cur=document.querySelector('.side-link.current');
if(cur){
 if(window.innerWidth>=1080){cur.scrollIntoView({block:'nearest'});}
 else if(window.innerWidth<=860){
  const nav=cur.parentElement;
  nav.scrollLeft=cur.offsetLeft-nav.offsetLeft-(nav.clientWidth-cur.clientWidth)/2;
 }
}
const imgs=document.querySelectorAll('img[src^="https:"]');
imgs.forEach(img=>img.addEventListener('error',()=>{
 if(img.dataset.fallback){img.src=img.dataset.fallback;delete img.dataset.fallback;}
 else{img.classList.add('image-failed');img.alt+=' (인터넷 연결 후 사진이 표시됩니다)';}
}));
})();
