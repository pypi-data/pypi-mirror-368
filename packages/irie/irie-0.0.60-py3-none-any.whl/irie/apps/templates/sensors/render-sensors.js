//===----------------------------------------------------------------------===//
//
//         STAIRLab -- STructural Artificial Intelligence Laboratory
//
//===----------------------------------------------------------------------===//
//
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

function createArrow(origin, direction, length, color, headLength, headWidth, shaftRadius) {
    const dir = direction.clone().normalize();

    const shaftLength = length - headLength;

    const arrowGroup = new THREE.Group();

    const shaftGeometry = new THREE.CylinderGeometry(shaftRadius, shaftRadius, shaftLength, 16);
    const shaftMaterial = new THREE.MeshStandardMaterial({ color: color });
    const shaftMesh = new THREE.Mesh(shaftGeometry, shaftMaterial);

    // CylinderGeometry is oriented along the Y-axis.
    // Rotate it so it aligns with the group's local +Y (arrow "up").
    // Then rotate the entire group to match `dir`.
    shaftMesh.position.y = shaftLength / 2;  // move it so its base starts at y=0
    arrowGroup.add(shaftMesh);

    const headGeometry = new THREE.ConeGeometry(shaftRadius * 2, headLength, 16);
    const headMaterial = new THREE.MeshStandardMaterial({ color: color });
    const headMesh = new THREE.Mesh(headGeometry, headMaterial);

    headMesh.position.y = shaftLength + headLength / 2;
    arrowGroup.add(headMesh);

    arrowGroup.position.copy(origin);

    // 5) Rotate the entire group so that +Y in local space points along `dir`
    const up = new THREE.Vector3(0, 1, 0);
    const quaternion = new THREE.Quaternion().setFromUnitVectors(up, dir);
    arrowGroup.quaternion.copy(quaternion);

    return arrowGroup;
}


function createSensorRenderer(container, modelPath) {

    // 1) SETUP SCENE
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // 2) SETUP RENDERER
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    // renderer.outputEncoding = THREE.sRGBEncoding; 
    container.appendChild(renderer.domElement);

    // 3) SETUP CAMERA
    const camera = new THREE.PerspectiveCamera(
        30,                                // fov
        container.clientWidth / container.clientHeight,  // aspect
        0.1,                               // near
        1000                               // far
    );
    // Position: "0deg 75deg 2m" => we can interpret as an angle from horizontal
    // Place the camera a bit above and away from the origin.
    camera.position.set(0, 2, 2);
    camera.lookAt(0, 0, 0);

    // 4) ORBIT CONTROLS
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);

    // 5) LIGHTING (basic environment)
    const ambientLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
    scene.add(ambientLight);

    const globalLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(globalLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    // directionalLight.position.set(5, 10, 7.5);
    directionalLight.position.set(100, 100, 100);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far  = 2000;
    directionalLight.shadow.camera.left   = -500; // was 500
    directionalLight.shadow.camera.right  =  500; // was 500
    directionalLight.shadow.camera.top    =  500; // was 500
    directionalLight.shadow.camera.bottom = -500; // was 500
    scene.add(directionalLight);

    // 6) LOAD THE GLB MODEL
    if (modelPath) {
        const loader = new GLTFLoader();
        loader.load(modelPath, (gltf) => {
            const model = gltf.scene;
            scene.add(model);

            // Compute bounding box
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3()).length();
            const center = box.getCenter(new THREE.Vector3());

            // Adjust camera clipping
            camera.near = size / 100;
            camera.far  = size * 100;
            camera.updateProjectionMatrix();

            // Move camera so the model is nicely framed
            camera.position.copy(center);
            // Move the camera out some distance (play with the multiplier)
            camera.position.x += size;  
            camera.position.y += size;  
            camera.position.z += size;  
            camera.lookAt(center);


            controls.target.copy(center);
            controls.update();
        },
        undefined,
        (error) => {
            console.error('Error loading GLB:', error);
        });

    } else {
        const axesHelper = new THREE.AxesHelper(1);
        scene.add(axesHelper);
    }

    // 7) HANDLE WINDOW RESIZE
    window.addEventListener('resize', onWindowResize, false);
    function onWindowResize() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }

    // 8) ANIMATE LOOP
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    return scene;
}
