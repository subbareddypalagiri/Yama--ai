'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

interface NeuralBackgroundProps {
  className?: string;
  particleCount?: number;
  connectionDistance?: number;
  speed?: number;
}

export default function NeuralBackground({
  className = '',
  particleCount = 800,
  connectionDistance = 120,
  speed = 0.3,
}: NeuralBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const linesRef = useRef<THREE.LineSegments | null>(null);
  const frameIdRef = useRef<number>(0);
  const mouseRef = useRef({ x: 0, y: 0 });
  const [isLowPerf, setIsLowPerf] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    // Performance detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isLowPerfDevice = isMobile || (navigator.hardwareConcurrency !== undefined && navigator.hardwareConcurrency < 4);
    setIsLowPerf(!!isLowPerfDevice);

    // Adjust particle count based on performance
    const actualParticleCount = isLowPerfDevice ? Math.floor(particleCount * 0.3) : particleCount;
    const actualConnectionDist = isLowPerfDevice ? connectionDistance * 0.7 : connectionDistance;

    // Setup
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 1, 2000);
    camera.position.z = 400;
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: !isLowPerfDevice,
      alpha: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Particle geometry
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(actualParticleCount * 3);
    const velocities = new Float32Array(actualParticleCount * 3);
    const colors = new Float32Array(actualParticleCount * 3);
    const sizes = new Float32Array(actualParticleCount);

    // Premium AI color palette - purple/pink/orange gradient
    const colorPalette = [
      new THREE.Color(0xA855F7), // Purple-500
      new THREE.Color(0xC084FC), // Purple-400
      new THREE.Color(0x8B5CF6), // Violet-500
      new THREE.Color(0xEC4899), // Pink-500
      new THREE.Color(0xF472B6), // Pink-400
      new THREE.Color(0xD946EF), // Fuchsia-500
      new THREE.Color(0xF97316), // Orange-500
      new THREE.Color(0xFB923C), // Orange-400
    ];

    for (let i = 0; i < actualParticleCount; i++) {
      const i3 = i * 3;

      // Spread particles in a sphere
      const radius = 300 + Math.random() * 200;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi) - 200;

      // Random velocities
      velocities[i3] = (Math.random() - 0.5) * speed;
      velocities[i3 + 1] = (Math.random() - 0.5) * speed;
      velocities[i3 + 2] = (Math.random() - 0.5) * speed * 0.5;

      // Colors - pick from premium palette
      const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;

      // Random sizes - slightly larger for more glow
      sizes[i] = Math.random() * 3 + 1;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    // Custom shader material for glowing particles with enhanced glow
    const particleMaterial = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        pixelRatio: { value: renderer.getPixelRatio() },
      },
      vertexShader: `
        attribute float size;
        attribute vec3 color;
        varying vec3 vColor;
        varying float vAlpha;
        uniform float time;
        
        void main() {
          vColor = color;
          
          vec3 pos = position;
          
          // Enhanced wave motion
          pos.x += sin(time * 0.4 + position.y * 0.008) * 3.0;
          pos.y += cos(time * 0.3 + position.x * 0.008) * 3.0;
          pos.z += sin(time * 0.2 + position.x * 0.005) * 2.0;
          
          vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
          
          // Size attenuation with pulsing
          float pulse = 1.0 + sin(time * 2.0 + position.x * 0.01) * 0.15;
          gl_PointSize = size * pulse * (320.0 / -mvPosition.z);
          gl_PointSize = max(gl_PointSize, 1.5);
          
          // Alpha based on depth
          vAlpha = smoothstep(-600.0, -100.0, mvPosition.z) * 0.9;
          
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        varying float vAlpha;
        
        void main() {
          // Soft circular particle with enhanced glow
          vec2 center = gl_PointCoord - vec2(0.5);
          float dist = length(center);
          
          if (dist > 0.5) discard;
          
          // Multi-layer glow effect
          float core = 1.0 - smoothstep(0.0, 0.15, dist);
          float glow = 1.0 - smoothstep(0.0, 0.5, dist);
          glow = pow(glow, 1.3);
          
          // Combine core brightness with outer glow
          float brightness = core * 0.5 + glow * 0.5;
          
          gl_FragColor = vec4(vColor, brightness * vAlpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const particles = new THREE.Points(geometry, particleMaterial);
    scene.add(particles);
    particlesRef.current = particles;

    // Lines geometry for connections with gradient colors
    const maxConnections = isLowPerfDevice ? 500 : 2000;
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = new Float32Array(maxConnections * 6);
    const lineColors = new Float32Array(maxConnections * 6);
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
    lineGeometry.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));
    lineGeometry.setDrawRange(0, 0);

    const lineMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
    });

    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);
    linesRef.current = lines;

    // Store velocities for animation
    (geometry as any).velocities = velocities;
    (geometry as any).actualConnectionDist = actualConnectionDist;
    (geometry as any).maxConnections = maxConnections;

    // Mouse tracking for interactivity
    const handleMouseMove = (event: MouseEvent) => {
      mouseRef.current.x = (event.clientX / width) * 2 - 1;
      mouseRef.current.y = -(event.clientY / height) * 2 + 1;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation
    let time = 0;
    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      time += 0.016;

      const positions = geometry.attributes.position.array as Float32Array;
      const velocities = (geometry as any).velocities as Float32Array;
      const connectionDist = (geometry as any).actualConnectionDist;
      const maxConns = (geometry as any).maxConnections;

      // Update particle positions
      for (let i = 0; i < actualParticleCount; i++) {
        const i3 = i * 3;

        positions[i3] += velocities[i3];
        positions[i3 + 1] += velocities[i3 + 1];
        positions[i3 + 2] += velocities[i3 + 2];

        // Boundary check - wrap around
        const bound = 500;
        if (positions[i3] > bound) positions[i3] = -bound;
        if (positions[i3] < -bound) positions[i3] = bound;
        if (positions[i3 + 1] > bound) positions[i3 + 1] = -bound;
        if (positions[i3 + 1] < -bound) positions[i3 + 1] = bound;
        if (positions[i3 + 2] > 200) positions[i3 + 2] = -400;
        if (positions[i3 + 2] < -400) positions[i3 + 2] = 200;
      }

      geometry.attributes.position.needsUpdate = true;
      (particleMaterial.uniforms.time as any).value = time;

      // Update connections with gradient colors
      if (!isLowPerfDevice || Math.floor(time * 60) % 3 === 0) {
        const linePositions = lineGeometry.attributes.position.array as Float32Array;
        const lineColors = lineGeometry.attributes.color.array as Float32Array;
        let connectionCount = 0;

        for (let i = 0; i < actualParticleCount && connectionCount < maxConns; i++) {
          const i3 = i * 3;
          const x1 = positions[i3];
          const y1 = positions[i3 + 1];
          const z1 = positions[i3 + 2];

          for (let j = i + 1; j < actualParticleCount && connectionCount < maxConns; j++) {
            const j3 = j * 3;
            const dx = x1 - positions[j3];
            const dy = y1 - positions[j3 + 1];
            const dz = z1 - positions[j3 + 2];
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

            if (dist < connectionDist) {
              const alpha = 1 - dist / connectionDist;
              const ci = connectionCount * 6;

              linePositions[ci] = x1;
              linePositions[ci + 1] = y1;
              linePositions[ci + 2] = z1;
              linePositions[ci + 3] = positions[j3];
              linePositions[ci + 4] = positions[j3 + 1];
              linePositions[ci + 5] = positions[j3 + 2];

              // Gradient line colors - purple to pink to orange based on position
              const colorMix = (Math.sin(time * 0.5 + i * 0.1) + 1) * 0.5;
              const intensity = alpha * 0.5;
              
              // Start color (purple-ish)
              lineColors[ci] = (0.66 + colorMix * 0.26) * intensity; // R
              lineColors[ci + 1] = (0.33 + colorMix * 0.15) * intensity; // G
              lineColors[ci + 2] = (0.97 - colorMix * 0.5) * intensity; // B
              
              // End color (more orange)
              lineColors[ci + 3] = (0.66 + colorMix * 0.32) * intensity;
              lineColors[ci + 4] = (0.33 + colorMix * 0.24) * intensity;
              lineColors[ci + 5] = (0.97 - colorMix * 0.6) * intensity;

              connectionCount++;
            }
          }
        }

        lineGeometry.setDrawRange(0, connectionCount * 2);
        lineGeometry.attributes.position.needsUpdate = true;
        lineGeometry.attributes.color.needsUpdate = true;
      }

      // Enhanced camera movement based on mouse
      camera.position.x += (mouseRef.current.x * 40 - camera.position.x) * 0.02;
      camera.position.y += (mouseRef.current.y * 40 - camera.position.y) * 0.02;
      camera.lookAt(scene.position);

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(frameIdRef.current);
      
      if (rendererRef.current) {
        rendererRef.current.dispose();
        container.removeChild(rendererRef.current.domElement);
      }
      
      geometry.dispose();
      particleMaterial.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
    };
  }, [particleCount, connectionDistance, speed]);

  return (
    <div
      ref={containerRef}
      className={`absolute inset-0 overflow-hidden ${className}`}
      style={{ 
        zIndex: 0,
        background: 'radial-gradient(ellipse at 50% 30%, #0a0810 0%, #030304 60%, #000000 100%)',
      }}
    >
      {/* Ambient glow overlays for depth */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(circle at 25% 25%, rgba(168, 85, 247, 0.03) 0%, transparent 40%),
            radial-gradient(circle at 75% 75%, rgba(236, 72, 153, 0.02) 0%, transparent 35%),
            radial-gradient(circle at 50% 80%, rgba(249, 115, 22, 0.02) 0%, transparent 30%)
          `,
        }}
      />
    </div>
  );
}
