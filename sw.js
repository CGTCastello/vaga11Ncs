// Service worker: permet instal·lar la web i consultar el calendari sense connexió.
// La pàgina es demana sempre primer a la xarxa, així els canvis del calendari arriben de seguida.
var CACHE = 'vaga11-v3';
var BASICS = ['./', 'es/', 'img/clau.png', 'img/icon-192.png', 'favicon.ico'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(BASICS); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

// Cada pàgina (valencià / castellà) es guarda a part, sense query ni àncora
function clau(req){
  if (req.mode !== 'navigate') return req;
  var u = new URL(req.url);
  return u.origin + u.pathname;
}

self.addEventListener('fetch', function(e){
  var req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith(
    fetch(req).then(function(res){
      // Només respostes completes (no els trossos de vídeo, 206)
      if (res.status === 200 && new URL(req.url).origin === location.origin) {
        var copia = res.clone();
        caches.open(CACHE).then(function(c){ c.put(clau(req), copia); });
      }
      return res;
    }).catch(function(){
      return caches.match(clau(req));
    })
  );
});
