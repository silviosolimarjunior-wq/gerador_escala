using UnityEngine;
using UnityEngine.AI;
public class RealisticZombieAI : MonoBehaviour
{     public enum ZombieState { Idle, Investigate, Chase };     public ZombieState currentState = ZombieState.Idle;     private NavMeshAgent agent;     private Transform player;     private Vector3 lastKnownNoisePosition;     public float visionRange = 10f;     public float visionAngle = 45f;     public LayerMask obstacleMask;     public LayerMask playerMask;     void Start()
}
cd ~/mata-zumbi
python3 -m http.server 8080
cd ~/mata-zumbi
cat << 'EOF' > index.html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zumbi FPS Mobile</title>
  <style>
    body { margin: 0; overflow: hidden; background: #050508; font-family: sans-serif; user-select: none; }
    #hud { position: absolute; top: 15px; left: 15px; color: #00ffcc; font-size: 18px; font-weight: bold; text-shadow: 2px 2px 4px #000; z-index: 10; }
    #ammo-hud { position: absolute; bottom: 25px; right: 35px; color: #ffaa00; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; z-index: 10; }
    #crosshair { position: absolute; top: 50%; left: 50%; width: 10px; height: 10px; background: rgba(0,255,204,0.9); border: 2px solid #fff; border-radius: 50%; transform: translate(-50%, -50%); z-index: 10; }
    #instructions { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,7,12,0.95); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; z-index: 20; text-align: center; }
    #instructions h1 { color: #ff2222; font-size: 34px; text-shadow: 0 0 15px #ff0000; }
    #touch-controls { position: absolute; bottom: 20px; left: 0; width: 100%; display: flex; justify-content: space-between; padding: 0 15px; box-sizing: border-box; z-index: 15; pointer-events: none; }
    .d-pad { display: grid; grid-template-columns: 60px 60px 60px; grid-template-rows: 60px 60px; gap: 5px; pointer-events: auto; }
    .t-btn { background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.5); border-radius: 12px; color: white; font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; touch-action: manipulation; }
    #btn-forward { grid-column: 2; grid-row: 1; }
    #btn-left { grid-column: 1; grid-row: 2; }
    #btn-backward { grid-column: 2; grid-row: 2; }
    #btn-right { grid-column: 3; grid-row: 2; }
    #btn-shoot { width: 85px; height: 85px; background: rgba(220,20,20,0.85); border: 3px solid #ff4444; border-radius: 50%; color: white; font-size: 36px; display: flex; align-items: center; justify-content: center; pointer-events: auto; touch-action: manipulation; }
  </style>
</head>
<body>
  <div id="hud">SAÚDE: <span id="health">100</span>% | ZUMBIS: <span id="score">0</span></div>
  <div id="ammo-hud">🔫 <span id="ammo">12</span>/12</div>
  <div id="crosshair"></div>
  <div id="instructions"><h1>ZUMBI FPS MOBILE</h1><p>Toque na tela para iniciar</p></div>
  <div id="touch-controls">
    <div class="d-pad">
      <div class="t-btn" id="btn-forward">▲</div>
      <div class="t-btn" id="btn-left">◀</div>
      <div class="t-btn" id="btn-backward">▼</div>
      <div class="t-btn" id="btn-right">▶</div>
    </div>
    <div id="btn-shoot">💥</div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0c12);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.6, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(10, 20, 10);
    scene.add(light);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), new THREE.MeshStandardMaterial({ color: 0x1b1f2b }));
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);

    const controls = new THREE.PointerLockControls(camera, document.body);
    document.getElementById('instructions').addEventListener('click', () => controls.lock());
    controls.addEventListener('lock', () => document.getElementById('instructions').style.display = 'none');
    controls.addEventListener('unlock', () => document.getElementById('instructions').style.display = 'flex');

    let moveF = false, moveB = false, moveL = false, moveR = false;
    const velocity = new THREE.Vector3();

    window.addEventListener('keydown', (e) => {
      if (e.code === 'KeyW') moveF = true;
      if (e.code === 'KeyS') moveB = true;
      if (e.code === 'KeyA') moveL = true;
      if (e.code === 'KeyD') moveR = true;
    });
    window.addEventListener('keyup', (e) => {
      if (e.code === 'KeyW') moveF = false;
      if (e.code === 'KeyS') moveB = false;
      if (e.code === 'KeyA') moveL = false;
      if (e.code === 'KeyD') moveR = false;
    });

    function bindTouch(id, onD, onU) {
      const el = document.getElementById(id);
      if(!el) return;
      el.addEventListener('touchstart', (e) => { e.preventDefault(); onD(); });
      el.addEventListener('touchend', (e) => { e.preventDefault(); onU(); });
    }
    bindTouch('btn-forward', () => moveF = true, () => moveF = false);
    bindTouch('btn-backward', () => moveB = true, () => moveB = false);
    bindTouchTouch = bindTouch('btn-left', () => moveL = true, () => moveL = false);
    bindTouch('btn-right', () => moveR = true, () => moveR = false);

    const zombies = [];
    function spawnZombie() {
      if (zombies.length >= 8) return;
      const group = new THREE.Group();
      // Corpo limpo e suave
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.8, 8), new THREE.MeshStandardMaterial({color: 0x446633}));
      body.position.y = 1.0;
      const head = new THREE.Mesh(new THREE.SphereGeometry(0.15, 8, 8), new THREE.MeshStandardMaterial({color: 0x557744}));
      head.position.y = 1.5;
      group.add(body, head);

      const angle = Math.random() * Math.PI * 2;
      group.position.set(camera.position.x + Math.sin(angle)*18, 0, camera.position.z + Math.cos(angle)*18);
      scene.add(group);
      zombies.push(group);
    }
    setInterval(spawnZombie, 2000);

    let score = 0, health = 100, ammo = 12;
    const raycaster = new THREE.Raycaster();

    function shoot() {
      if (ammo <= 0) return;
      ammo--;
      document.getElementById('ammo').innerText = ammo;

      raycaster.setFromCamera(new THREE.Vector2(0,0), camera);
      const hits = raycaster.intersectObjects(scene.children, true);
      for(let hit of hits) {
        let obj = hit.object;
        while(obj.parent && obj.parent !== scene) obj = obj.parent;
        if(zombies.includes(obj)) {
          scene.remove(obj);
          zombies.splice(zombies.indexOf(obj), 1);
          score++;
          document.getElementById('score').innerText = score;
          break;
        }
      }
    }
    document.getElementById('btn-shoot').addEventListener('click', (e) => { e.stopPropagation(); shoot(); });
    window.addEventListener('mousedown', () => { if(controls.isLocked) shoot(); });

    let prevT = performance.now();
    function animate() {
      requestAnimationFrame(animate);
      const now = performance.now();
      const delta = (now - prevT) / 1000;
      prevT = now;

      if (controls.isLocked || moveF || moveB || moveL || moveR) {
        velocity.set(0,0,0);
        if (moveF) velocity.z -= 5;
        if (moveB) velocity.z += 5;
        if (moveL) velocity.x -= 5;
        if (moveR) velocity.x += 5;
        controls.moveRight(-velocity.x * delta);
        controls.moveForward(-velocity.z * delta);

        zombies.forEach(z => {
          z.lookAt(camera.position.x, z.position.y, camera.position.z);
          z.translateZ(2 * delta);
          if (z.position.distanceTo(camera.position) < 1.2) {
            health -= 0.5;
            document.getElementById('health').innerText = Math.max(0, Math.round(health));
            if(health <= 0) { alert('Game Over!'); location.reload(); }
          }
        });
      }
      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>
EOF

python3 -m http.server 8080
python3 -c "
html = '''<!DOCTYPE html>
<html lang=\\'pt-br\\'>
<head>
  <meta charset=\\'UTF-8\\'>
  <meta name=\\'viewport\\' content=\\'width=device-width, initial-scale=1.0\\'>
  <title>Zumbi FPS Mobile</title>
  <style>
    body { margin: 0; overflow: hidden; background: #050508; font-family: sans-serif; user-select: none; }
    #hud { position: absolute; top: 15px; left: 15px; color: #00ffcc; font-size: 18px; font-weight: bold; text-shadow: 2px 2px 4px #000; z-index: 10; }
    #ammo-hud { position: absolute; bottom: 25px; right: 35px; color: #ffaa00; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; z-index: 10; }
    #crosshair { position: absolute; top: 50%; left: 50%; width: 10px; height: 10px; background: rgba(0,255,204,0.9); border: 2px solid #fff; border-radius: 50%; transform: translate(-50%, -50%); z-index: 10; }
    #instructions { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,7,12,0.95); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; z-index: 20; text-align: center; }
    #instructions h1 { color: #ff2222; font-size: 34px; text-shadow: 0 0 15px #ff0000; }
    #touch-controls { position: absolute; bottom: 20px; left: 0; width: 100%; display: flex; justify-content: space-between; padding: 0 15px; box-sizing: border-box; z-index: 15; pointer-events: none; }
    .d-pad { display: grid; grid-template-columns: 60px 60px 60px; grid-template-rows: 60px 60px; gap: 5px; pointer-events: auto; }
    .t-btn { background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.5); border-radius: 12px; color: white; font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; touch-action: manipulation; }
    #btn-forward { grid-column: 2; grid-row: 1; }
    #btn-left { grid-column: 1; grid-row: 2; }
    #btn-backward { grid-column: 2; grid-row: 2; }
    #btn-right { grid-column: 3; grid-row: 2; }
    #btn-shoot { width: 85px; height: 85px; background: rgba(220,20,20,0.85); border: 3px solid #ff4444; border-radius: 50%; color: white; font-size: 36px; display: flex; align-items: center; justify-content: center; pointer-events: auto; touch-action: manipulation; }
  </style>
</head>
<body>
  <div id=\\'hud\\'>SAÚDE: <span id=\\'health\\'>100</span>% | ZUMBIS: <span id=\\'score\\'>0</span></div>
  <div id=\\'ammo-hud\\'>🔫 <span id=\\'ammo\\'>12</span>/12</div>
  <div id=\\'crosshair\\'></div>
  <div id=\\'instructions\\'><h1>ZUMBI FPS MOBILE</h1><p>Toque na tela para iniciar</p></div>
  <div id=\\'touch-controls\\'>
    <div class=\\'d-pad\\'>
      <div class=\\'t-btn\\' id=\\'btn-forward\\'>▲</div>
      <div class=\\'t-btn\\' id=\\'btn-left\\'>◀</div>
      <div class=\\'t-btn\\' id=\\'btn-backward\\'>▼</div>
      <div class=\\'t-btn\\' id=\\'btn-right\\'>▶</div>
    </div>
    <div id=\\'btn-shoot\\'>💥</div>
  </div>

  <script src=\\'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js\\'></script>
  <script src=\\'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js\\'></script>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0c12);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.6, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(10, 20, 10);
    scene.add(light);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), new THREE.MeshStandardMaterial({ color: 0x1b1f2b }));
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);

    const controls = new THREE.PointerLockControls(camera, document.body);
    document.getElementById('instructions').addEventListener('click', () => controls.lock());
    controls.addEventListener('lock', () => document.getElementById('instructions').style.display = 'none');
    controls.addEventListener('unlock', () => document.getElementById('instructions').style.display = 'flex');

    let moveF = false, moveB = false, moveL = false, moveR = false;
    const velocity = new THREE.Vector3();

    window.addEventListener('keydown', (e) => {
      if (e.code === 'KeyW') moveF = true;
      if (e.code === 'KeyS') moveB = true;
      if (e.code === 'KeyA') moveL = true;
      if (e.code === 'KeyD') moveR = true;
    });
    window.addEventListener('keyup', (e) => {
      if (e.code === 'KeyW') moveF = false;
      if (e.code === 'KeyS') moveB = false;
      if (e.code === 'KeyA') moveL = false;
      if (e.code === 'KeyD') moveR = false;
    });

    function bindTouch(id, onD, onU) {
      const el = document.getElementById(id);
      el.addEventListener('touchstart', (e) => { e.preventDefault(); onD(); });
      el.addEventListener('touchend', (e) => { e.preventDefault(); onU(); });
    }
    bindTouch('btn-forward', () => moveF = true, () => moveF = false);
    bindTouch('btn-backward', () => moveB = true, () => moveB = false);
    bindTouch('btn-left', () => moveL = true, () => moveL = false);
    bindTouch('btn-right', () => moveR = true, () => moveR = false);

    const zombies = [];
    function spawnZombie() {
      if (zombies.length >= 8) return;
      const group = new THREE.Group();
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.8, 8), new THREE.MeshStandardMaterial({color: 0x446633}));
      body.position.y = 1.0;
      const head = new THREE.Mesh(new THREE.SphereGeometry(0.15, 8, 8), new THREE.MeshStandardMaterial({color: 0x557744}));
      head.position.y = 1.5;
      group.add(body, head);

      const angle = Math.random() * Math.PI * 2;
      group.position.set(camera.position.x + Math.sin(angle)*18, 0, camera.position.z + Math.cos(angle)*18);
      scene.add(group);
      zombies.push(group);
    }
    setInterval(spawnZombie, 2000);

    let score = 0, health = 100, ammo = 12;
    const raycaster = new THREE.Raycaster();

    function shoot() {
      if (ammo <= 0) return;
      ammo--;
      document.getElementById('ammo').innerText = ammo;

      raycaster.setFromCamera(new THREE.Vector2(0,0), camera);
      const hits = raycaster.intersectObjects(scene.children, true);
      for(let hit of hits) {
        let obj = hit.object;
        while(obj.parent && obj.parent !== scene) obj = obj.parent;
        if(zombies.includes(obj)) {
          scene.remove(obj);
          zombies.splice(zombies.indexOf(obj), 1);
          score++;
          document.getElementById('score').innerText = score;
          break;
        }
      }
    }
    document.getElementById('btn-shoot').addEventListener('click', (e) => { e.stopPropagation(); shoot(); });
    window.addEventListener('mousedown', () => { if(controls.isLocked) shoot(); });

    let prevT = performance.now();
    function animate() {
      requestAnimationFrame(animate);
      const now = performance.now();
      const delta = (now - prevT) / 1000;
      prevT = now;

      if (controls.isLocked || moveF || moveB || moveL || moveR) {
        velocity.set(0,0,0);
        if (moveF) velocity.z -= 5;
        if (moveB) velocity.z += 5;
        if (moveL) velocity.x -= 5;
        if (moveR) velocity.x += 5;
        controls.moveRight(-velocity.x * delta);
        controls.moveForward(-velocity.z * delta);

        zombies.forEach(z => {
          z.lookAt(camera.position.x, z.position.y, camera.position.z);
          z.translateZ(2 * delta);
          if (z.position.distanceTo(camera.position) < 1.2) {
            health -= 0.5;
            document.getElementById('health').innerText = Math.max(0, Math.round(health));
            if(health <= 0) { alert('Game Over!'); location.reload(); }
          }
        });
      }
      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>
'''
with open('index.html', 'w') as f:
    f.write(html)
print('Ficheiro criado com sucesso!')
"
python3 -m http.server 8080
cat << 'EOF' > teste.txt
Linha 1: Aprendendo Python
Linha 2: Erro no código
Linha 3: Estudando lógica
Linha 4: Erro no código
Linha 5: Praticando comandos
EOF

cat teste.txt
sed -i 's/Erro no código//g' teste.txt
cat teste.txt
sed -i '/Erro no código/d' teste.txt
sed
in-place).
​'/Erro no código/d':
d
pkg install git -y
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
git init
git add .
git commit -m "feat: adiciona integracao inicial de IA ao CRM com Flask"
git branch -M main
git remote add origin https://github.com/seu-usuario/nome-do-repositorio.git
git push -u origin main
