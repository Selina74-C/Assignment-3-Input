const audioUrl = './matplotlib_music.wav';
const canvas = document.getElementById('vis');
const ctx = canvas.getContext('2d');
let cw, ch;
function resize(){cw = canvas.width = innerWidth; ch = canvas.height = innerHeight}
addEventListener('resize', resize); resize();

const AudioContext = window.AudioContext || window.webkitAudioContext;
const actx = new AudioContext();
let source, gainNode, analyser;
const particles = [];

function createAnalyser(){
	analyser = actx.createAnalyser();
	analyser.fftSize = 1024;
	analyser.smoothingTimeConstant = 0.85;
	gainNode = actx.createGain();
	gainNode.gain.value = 0.9;
}

async function loadAndDecode(){
	createAnalyser();
	const res = await fetch(audioUrl);
	const ab = await res.arrayBuffer();
	const buffer = await actx.decodeAudioData(ab.slice(0));
	return buffer;
}

function makeSource(buffer){
	if(source) try{ source.stop(); }catch(e){}
	source = actx.createBufferSource();
	source.buffer = buffer;
	source.loop = document.getElementById('loop').checked;
	source.connect(gainNode).connect(analyser).connect(actx.destination);
}

function spawnParticles(energy){
	const count = Math.min(16, Math.round(energy * 20));
	for(let i=0;i<count;i++){
		particles.push({
			x: cw/2 + (Math.random()-0.5)*200,
			y: ch/2 + (Math.random()-0.5)*200,
			vx: (Math.random()-0.5)*4,
			vy: (Math.random()-0.5)*4,
			life: 60 + Math.random()*60,
			r: 2+Math.random()*6,
			hue: Math.floor(200 + Math.random()*60)
		});
	}
}

function draw(){
	ctx.clearRect(0,0,cw,ch);
	// get spectrum
	const data = new Uint8Array(analyser.frequencyBinCount);
	analyser.getByteFrequencyData(data);
	let sum=0;
	for(let i=0;i<data.length;i++){ sum += data[i]; }
	const energy = sum / (data.length*255);

	// draw background radial
	const grad = ctx.createRadialGradient(cw/2,ch/2,0,cw/2,ch/2,Math.max(cw,ch));
	grad.addColorStop(0, `rgba(20,24,40,${0.25+energy*0.6})`);
	grad.addColorStop(1, '#03040a');
	ctx.fillStyle = grad; ctx.fillRect(0,0,cw,ch);

	// central pulsating circle
	ctx.beginPath();
	const radius = 60 + energy*420;
	ctx.arc(cw/2, ch/2, radius, 0, Math.PI*2);
	ctx.fillStyle = `hsla(${200+energy*120},80%,60%,${0.06+energy*0.6})`;
	ctx.fill();

	// waveform ring
	ctx.beginPath();
	const bins = 120;
	for(let i=0;i<bins;i++){
		const v = data[Math.floor(i*(data.length/bins))]/255;
		const ang = (i/bins)*Math.PI*2 - Math.PI/2;
		const r = radius + v*140;
		const x = cw/2 + Math.cos(ang)*r;
		const y = ch/2 + Math.sin(ang)*r;
		if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
	}
	ctx.closePath();
	ctx.strokeStyle = `hsla(${220+energy*100},70%,65%,${0.8})`;
	ctx.lineWidth = 2;
	ctx.stroke();

	// spawn particles
	if(energy>0.02) spawnParticles(energy);

	// update particles
	for(let i=particles.length-1;i>=0;i--){
		const p = particles[i];
		p.x += p.vx; p.y += p.vy; p.life -= 1;
		p.vy += 0.02;
		const alpha = Math.max(0, p.life/120);
		ctx.beginPath();
		ctx.fillStyle = `hsla(${p.hue},80%,60%,${alpha})`;
		ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
		ctx.fill();
		if(p.life<=0) particles.splice(i,1);
	}

	requestAnimationFrame(draw);
}

let decodedBuffer = null;
loadAndDecode().then(buf=>{ decodedBuffer = buf; makeSource(buf); document.getElementById('play').disabled=false; });

document.getElementById('play').addEventListener('click', async ()=>{
	if(actx.state==='suspended') await actx.resume();
	if(!decodedBuffer) return;
	makeSource(decodedBuffer);
	const vol = document.getElementById('volume').value; gainNode.gain.value = vol;
	source.start();
	draw();
});
document.getElementById('pause').addEventListener('click', ()=>{ try{ source.stop(); }catch(e){} });
document.getElementById('loop').addEventListener('change', ()=>{ if(source) source.loop = document.getElementById('loop').checked; });
document.getElementById('volume').addEventListener('input', (e)=>{ if(gainNode) gainNode.gain.value = e.target.value });

