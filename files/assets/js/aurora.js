(() => {
	'use strict';

	const layer = document.getElementById('obsession-aurora');
	if (!layer || layer.dataset.initialized === 'true') return;
	layer.dataset.initialized = 'true';

	const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
	if (motionQuery.matches) {
		layer.dataset.mode = 'static';
		return;
	}

	const canvas = document.createElement('canvas');
	canvas.setAttribute('aria-hidden', 'true');
	const gl = canvas.getContext('webgl', {
		alpha: true,
		antialias: false,
		depth: false,
		stencil: false,
		premultipliedAlpha: true,
		preserveDrawingBuffer: false,
		powerPreference: 'low-power'
	});

	if (!gl) {
		layer.dataset.mode = 'static';
		return;
	}

	const vertexSource = `
		attribute vec2 position;
		void main() {
			gl_Position = vec4(position, 0.0, 1.0);
		}
	`;

	const fragmentSource = `
		precision highp float;

		uniform float uTime;
		uniform float uAmplitude;
		uniform vec2 uResolution;
		uniform float uBlend;
		uniform vec3 uColorStops[3];

		vec3 permute(vec3 x) {
			return mod(((x * 34.0) + 1.0) * x, 289.0);
		}

		float snoise(vec2 v) {
			const vec4 C = vec4(
				0.211324865405187, 0.366025403784439,
				-0.577350269189626, 0.024390243902439
			);
			vec2 i = floor(v + dot(v, C.yy));
			vec2 x0 = v - i + dot(i, C.xx);
			vec2 i1 = x0.x > x0.y ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
			vec4 x12 = x0.xyxy + C.xxzz;
			x12.xy -= i1;
			i = mod(i, 289.0);
			vec3 p = permute(
				permute(i.y + vec3(0.0, i1.y, 1.0))
				+ i.x + vec3(0.0, i1.x, 1.0)
			);
			vec3 m = max(0.5 - vec3(
				dot(x0, x0),
				dot(x12.xy, x12.xy),
				dot(x12.zw, x12.zw)
			), 0.0);
			m = m * m;
			m = m * m;
			vec3 x = 2.0 * fract(p * C.www) - 1.0;
			vec3 h = abs(x) - 0.5;
			vec3 ox = floor(x + 0.5);
			vec3 a0 = x - ox;
			m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
			vec3 g;
			g.x = a0.x * x0.x + h.x * x0.y;
			g.yz = a0.yz * x12.xz + h.yz * x12.yw;
			return 130.0 * dot(m, g);
		}

		void main() {
			vec2 uv = gl_FragCoord.xy / uResolution;
			vec3 leftColor = uColorStops[0];
			vec3 middleColor = uColorStops[1];
			vec3 rightColor = uColorStops[2];
			vec3 rampColor = uv.x < 0.5
				? mix(leftColor, middleColor, uv.x * 2.0)
				: mix(middleColor, rightColor, (uv.x - 0.5) * 2.0);

			float wave = snoise(vec2(uv.x * 1.65 + uTime * 0.08, uTime * 0.18));
			float height = exp(wave * 0.5 * uAmplitude);
			float intensity = 0.48 * (uv.y * 1.8 - height + 0.42);
			float alpha = smoothstep(0.20 - uBlend * 0.5, 0.20 + uBlend * 0.5, intensity);
			alpha *= smoothstep(0.0, 0.18, uv.y) * (1.0 - smoothstep(0.82, 1.0, uv.y));

			vec3 color = max(intensity, 0.0) * rampColor;
			gl_FragColor = vec4(color * alpha, alpha * 0.72);
		}
	`;

	function compile(type, source) {
		const shader = gl.createShader(type);
		gl.shaderSource(shader, source);
		gl.compileShader(shader);
		if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
			const message = gl.getShaderInfoLog(shader);
			gl.deleteShader(shader);
			throw new Error(message || 'Aurora shader compilation failed');
		}
		return shader;
	}

	let program;
	try {
		program = gl.createProgram();
		const vertexShader = compile(gl.VERTEX_SHADER, vertexSource);
		const fragmentShader = compile(gl.FRAGMENT_SHADER, fragmentSource);
		gl.attachShader(program, vertexShader);
		gl.attachShader(program, fragmentShader);
		gl.linkProgram(program);
		gl.deleteShader(vertexShader);
		gl.deleteShader(fragmentShader);
		if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
			throw new Error(gl.getProgramInfoLog(program) || 'Aurora shader linking failed');
		}
	} catch (error) {
		console.warn('Ambient background unavailable:', error);
		layer.dataset.mode = 'static';
		gl.getExtension('WEBGL_lose_context')?.loseContext();
		return;
	}

	const buffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

	gl.useProgram(program);
	const position = gl.getAttribLocation(program, 'position');
	gl.enableVertexAttribArray(position);
	gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

	const uniforms = {
		time: gl.getUniformLocation(program, 'uTime'),
		amplitude: gl.getUniformLocation(program, 'uAmplitude'),
		resolution: gl.getUniformLocation(program, 'uResolution'),
		blend: gl.getUniformLocation(program, 'uBlend'),
		colors: gl.getUniformLocation(program, 'uColorStops')
	};

	gl.uniform1f(uniforms.amplitude, 0.44);
	gl.uniform1f(uniforms.blend, 0.88);
	gl.uniform3fv(uniforms.colors, new Float32Array([
		0.035, 0.002, 0.006,
		0.25, 0.008, 0.025,
		0.045, 0.002, 0.008
	]));
	gl.clearColor(0, 0, 0, 0);
	gl.enable(gl.BLEND);
	gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

	layer.appendChild(canvas);
	layer.dataset.mode = 'webgl';

	let frameId = 0;
	let lastFrame = 0;
	let hidden = document.hidden;
	let destroyed = false;

	function resize() {
		const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
		const width = Math.max(1, Math.round(layer.clientWidth * ratio));
		const height = Math.max(1, Math.round(layer.clientHeight * ratio));
		if (canvas.width === width && canvas.height === height) return;
		canvas.width = width;
		canvas.height = height;
		canvas.style.width = '100%';
		canvas.style.height = '100%';
		gl.viewport(0, 0, width, height);
		gl.uniform2f(uniforms.resolution, width, height);
	}

	function render(time) {
		if (destroyed) return;
		frameId = window.requestAnimationFrame(render);
		if (hidden || time - lastFrame < 33) return;
		lastFrame = time;
		resize();
		gl.uniform1f(uniforms.time, time * 0.000035);
		gl.drawArrays(gl.TRIANGLES, 0, 3);
	}

	function onVisibilityChange() {
		hidden = document.hidden;
	}

	function destroy() {
		if (destroyed) return;
		destroyed = true;
		window.cancelAnimationFrame(frameId);
		window.removeEventListener('resize', resize);
		document.removeEventListener('visibilitychange', onVisibilityChange);
		window.removeEventListener('pagehide', destroy);
		motionQuery.removeEventListener?.('change', onMotionChange);
		if (canvas.parentNode === layer) layer.removeChild(canvas);
		gl.deleteBuffer(buffer);
		gl.deleteProgram(program);
		gl.getExtension('WEBGL_lose_context')?.loseContext();
		delete layer.dataset.initialized;
	}

	function onMotionChange(event) {
		if (event.matches) {
			layer.dataset.mode = 'static';
			destroy();
		}
	}

	window.addEventListener('resize', resize, { passive: true });
	document.addEventListener('visibilitychange', onVisibilityChange);
	window.addEventListener('pagehide', destroy, { once: true });
	motionQuery.addEventListener?.('change', onMotionChange);

	resize();
	frameId = window.requestAnimationFrame(render);
})();
