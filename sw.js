// Service worker: permet instal·lar la web i consultar el calendari sense connexió.
// La pàgina es demana sempre primer a la xarxa, així els canvis del calendari arriben de seguida.
var CACHE = 'vaga11-v1';
var BASICS = ['./', 'img/clau.png', 'img/icon-192.png', 'favicon.ico'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(BASICS); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener('fetch', function(e){
  var req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith(
    fetch(req).then(function(res){
      if (res.ok && new URL(req.url).origin === location.origin) {
        var copia = res.clone();
        caches.open(CACHE).then(function(c){ c.put(req.mode === 'navigate' ? './' : req, copia); });
      }
      return res;
    }).catch(function(){
      return caches.match(req.mode === 'navigate' ? './' : req);
    })
  );
});
