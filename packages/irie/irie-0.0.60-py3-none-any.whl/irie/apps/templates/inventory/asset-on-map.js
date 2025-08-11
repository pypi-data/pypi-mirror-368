//===----------------------------------------------------------------------===#
//
//         STAIRLab -- STructural Artificial Intelligence Laboratory
//
//===----------------------------------------------------------------------===#
//
//
function createAssetLayerThreeJS(options) {
    const {map, modelSource, modelOrigin, modelRotate, unitToMeter} = options;
    const modelAltitude = 0;
    const modelCoord = maplibregl.MercatorCoordinate.fromLngLat(
        modelOrigin,
        modelAltitude
    );
    const modelScale = modelCoord.meterInMercatorCoordinateUnits()*unitToMeter;
    const modelTransform = {
        translateX: modelCoord.x,
        translateY: modelCoord.y, //-25*modelScale,
        translateZ: modelCoord.z+35*modelScale, // 100*modelScale, // 35
        rotateX: modelRotate[0],
        rotateY: modelRotate[1],
        rotateZ: modelRotate[2],
        scale: modelScale
    };

    return {
        id: '3d-model',
        type: 'custom',
        renderingMode: '3d',
        onAdd(map, gl) {
            this.camera = new THREE.Camera();
            this.scene = new THREE.Scene();

            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(100, 100, 100);
            directionalLight.castShadow = true;
            this.scene.add(directionalLight);

            directionalLight.shadow.camera.near = 0.1;
            directionalLight.shadow.camera.far  = 2000;
            directionalLight.shadow.camera.left   = -50000; // was 500
            directionalLight.shadow.camera.right  =  50000; // was 500
            directionalLight.shadow.camera.top    =  50000; // was 500
            directionalLight.shadow.camera.bottom = -50000; // was 500

            directionalLight.shadow.mapSize.width  = 4096;
            directionalLight.shadow.mapSize.height = 4096;

            const groundGeometry = new THREE.PlaneGeometry(5000, 5000);
            const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = - 100; // 35;
            ground.receiveShadow = true;
            this.scene.add(ground);

            const loader = new GLTFLoader();
            loader.load(
                modelSource,
                (gltf) => {
                    gltf.scene.traverse(function (node) {
                        if (node.isMesh || node.isLight) {
                            node.castShadow = true;
                            node.receiveShadow = true;
                        }
                    });
                    this.scene.add(gltf.scene);
                }
            );
            this.map = map;

            this.renderer = new THREE.WebGLRenderer({
                canvas: map.getCanvas(),
                context: gl,
                antialias: true
            });
            this.renderer.shadowMap.enabled = true;
            this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            this.renderer.autoClear = false;
        },
        render(gl, args) {
            const rotationX = new THREE.Matrix4().makeRotationAxis(
                new THREE.Vector3(1, 0, 0),
                modelTransform.rotateX
            );
            const rotationY = new THREE.Matrix4().makeRotationAxis(
                new THREE.Vector3(0, 1, 0),
                modelTransform.rotateY
            );
            const rotationZ = new THREE.Matrix4().makeRotationAxis(
                new THREE.Vector3(0, 0, 1),
                modelTransform.rotateZ
            );

            const m = new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix);
            const l = new THREE.Matrix4()
                .makeTranslation(
                    modelTransform.translateX,
                    modelTransform.translateY,
                    modelTransform.translateZ
                )
                .scale(
                    new THREE.Vector3(
                        modelTransform.scale,
                        -modelTransform.scale,
                        modelTransform.scale
                    )
                )
                .multiply(rotationX)
                .multiply(rotationY)
                .multiply(rotationZ);

            this.camera.projectionMatrix = m.multiply(l);
            this.renderer.resetState();
            this.renderer.render(this.scene, this.camera);
            this.map.triggerRepaint();
        }
    };
}

function createAssetLayerBabylon(options) {
    const {map, modelSource, modelOrigin, modelRotate, unitToMeter} = options;
    const worldAltitude = 0;

    const BABYLON = window.BABYLON;
    // +x east, +y up, +z north
    // const modelRotate = [Math.PI / 2, 0, 0];
    // Maplibre.js default coordinate system (no rotations)
    // +x east, -y north, +z up
    //var worldRotate = [0, 0, 0];

    const worldOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(
        modelOrigin,
        worldAltitude
    );
    const modelScale = worldOriginMercator.meterInMercatorCoordinateUnits()*unitToMeter;
    const modelTransform = {
            translateX: worldOriginMercator.x,
            translateY: worldOriginMercator.y-25*modelScale,
            translateZ: worldOriginMercator.z+35*modelScale,
            rotateX: modelRotate[0],
            rotateY: modelRotate[1],
            rotateZ: modelRotate[2],
            scale: modelScale
    };

    // Calculate world matrix
    const worldMatrix = BABYLON.Matrix.Compose(
        new BABYLON.Vector3(modelScale, modelScale, modelScale),
        BABYLON.Quaternion.FromEulerAngles(
            modelRotate[0],
            modelRotate[1],
            modelRotate[2]
        ),
        new BABYLON.Vector3(
            worldOriginMercator.x,
            worldOriginMercator.y,
            worldOriginMercator.z
        )
    );

    return {
        id: '3d-model',
        type: 'custom',
        renderingMode: '3d',
        onAdd (map, gl) {
            this.engine = new BABYLON.Engine(
                gl,
                true,
                {
                    useHighPrecisionMatrix: true // Important to prevent jitter at mercator scale
                },
                true
            );
            this.scene = new BABYLON.Scene(this.engine);
            /**
            * optionally add
            * this.scene.autoClearDepthAndStencil = false
            * and for renderingGroupIds set this individually via
            * this.scene.setRenderingAutoClearDepthStencil(1,false)
            * to allow blending with maplibre scene
            * as documented in https://doc.babylonjs.com/features/featuresDeepDive/scene/optimize_your_scene#reducing-calls-to-glclear
            */
            this.scene.autoClear = false;
            /**
            * use detachControl if you only want to interact with maplibre-gl and do not need pointer events of babylonjs.
            * alternatively exchange this.scene.detachControl() with the following two lines, they will allow bubbling up events to maplibre-gl.
            * this.scene.preventDefaultOnPointerDown = false
            * this.scene.preventDefaultOnPointerUp = false
            * https://doc.babylonjs.com/typedoc/classes/BABYLON.Scene#preventDefaultOnPointerDown
            */
            this.scene.detachControl();

            this.scene.beforeRender = () => {
                this.engine.wipeCaches(true);
            };

            // create simple camera (will have its project matrix manually calculated)
            this.camera = new BABYLON.Camera(
                'Camera',
                new BABYLON.Vector3(0, 0, 0),
                this.scene
            );

            // create simple light
            const light = new BABYLON.HemisphericLight(
                'light1',
                new BABYLON.Vector3(0, 0, 100),
                this.scene
            );
            light.intensity = 0.7;

            // Add debug axes viewer, positioned at origin, 10 meter axis lengths
            new BABYLON.AxesViewer(this.scene, 10);

            // load GLTF model in to the scene
            BABYLON.SceneLoader.LoadAssetContainerAsync(
                modelSource, '', this.scene
            ).then((modelContainer) => {
                modelContainer.addAllToScene();

                const rootMesh = modelContainer.createRootMesh();

                // If using maplibre.js coordinate system (+z up)
                // rootMesh.rotation.x = Math.PI/2

                // // Create a second mesh
                // const rootMesh2 = rootMesh.clone();

                // // Position in babylon.js coordinate system
                // rootMesh2.position.x = 25; // +east, meters
                // rootMesh2.position.z = 25; // +north, meters
            });

            this.map = map;
        },
        render (gl, args) {
            const cameraMatrix = BABYLON.Matrix.FromArray(args.defaultProjectionData.mainMatrix);

            // world-view-projection matrix
            const wvpMatrix = worldMatrix.multiply(cameraMatrix);

            this.camera.freezeProjectionMatrix(wvpMatrix);

            this.scene.render(false);
            this.map.triggerRepaint();
        }
    };

}

/*
* Helper function used to get threejs-scene-coordinates from mercator coordinates.
* This is just a quick and dirty solution - it won't work if points are far away from each other
* because a meter near the north-pole covers more mercator-units
* than a meter near the equator.
*/
function calculateDistanceMercatorToMeters(from, to) {
    const mercatorPerMeter = from.meterInMercatorCoordinateUnits();
    // mercator x: 0=west, 1=east
    const dEast = to.x - from.x;
    const dEastMeter = dEast / mercatorPerMeter;
    // mercator y: 0=north, 1=south
    const dNorth = from.y - to.y;
    const dNorthMeter = dNorth / mercatorPerMeter;
    return {dEastMeter, dNorthMeter};
}

document.addEventListener('DOMContentLoaded', () => {
    const div = document.querySelector('#map');
    const modelOrigin = JSON.parse(div.dataset.location); // [-124.1014, 40.50303];
    var modelSource = undefined;
    if (div.dataset.renderSource)
        modelSource = div.dataset.renderSource;
    else
        modelSource = div.dataset.renderInline;

    const unitToMeter = 1/3.2808;

    const MAPTILER_KEY = 'get_your_own_OpIi9ZULNHzrESv6T2vL';
    const mapid = 'winter'; // 'dataviz'; // 'basic-v2'; // 'aquarelle';
    const map = (window.map = new maplibregl.Map({
        container: 'map',
        style: `https://api.maptiler.com/maps/${mapid}/style.json?key=${MAPTILER_KEY}`,
        zoom: 18,
        center: modelOrigin,
        zoom: 18,
        maxZoom: 30,
        maxPitch: 85,
        pitch: 77,
        // create the gl context with MSAA antialiasing, so custom layers are antialiased
        canvasContextAttributes: {antialias: true}
    }));

    // Make interaction the same as THREE OrbitControls
    map.dragPan.disable();
    map.dragRotate.enable({ pitchWithRotate: true });
    map.scrollZoom.enable({ around: 'pointer' });
    map.dragPan.enable({
    deceleration: 2000,   // px/s²
    linearity:   0.3,     // lower = snappier stop
    maxSpeed:    2000
    });
    map.scrollZoom.setWheelZoomRate(1/600);  // slower mouse‐wheel zoom
    map.keyboard.enable();                   // arrow keys to pan/zoom
    map.touchZoomRotate.enable();            // two-finger pinch & rotate


    //
    // Add Buildings
    //

    // The 'building' layer in the streets vector source contains building-height
    // data from OpenStreetMap.
    map.on('load', () => {
        // Insert the layer beneath any symbol layer.
        const layers = map.getStyle().layers;

        let labelLayerId;
        for (let i = 0; i < layers.length; i++) {
            if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
                labelLayerId = layers[i].id;
                break;
            }
        }

        map.addSource('openmaptiles', {
            url: `https://api.maptiler.com/tiles/v3/tiles.json?key=${MAPTILER_KEY}`,
            type: 'vector',
        });

        map.addLayer(
            {
                'id': '3d-buildings',
                'source': 'openmaptiles',
                'source-layer': 'building',
                'type': 'fill-extrusion',
                'minzoom': 15,
                'filter': ['!=', ['get', 'hide_3d'], true],
                'paint': {
                    'fill-extrusion-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'render_height'], 0, 'lightgray', 200, 'royalblue', 400, 'lightblue'
                    ],
                    'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        16,
                        ['get', 'render_height']
                    ],
                    'fill-extrusion-base': ['case',
                        ['>=', ['get', 'zoom'], 16],
                        ['get', 'render_min_height'], 0
                    ]
                }
            },
            labelLayerId
        );
    });


    //
    // Add Asset
    //
    const worldAltitude = 0;
    // +x east, +y up, +z north
    const modelRotate = [Math.PI / 2, 0, 0];
    // Maplibre.js default coordinate system (no rotations)
    // +x east, -y north, +z up
    // const modelRotate = [0, 0, 0];

    map.on('style.load', () => {
    {% if viewer == "three" %}
        map.addLayer(createAssetLayerThreeJS({
    {% else %}
        map.addLayer(createAssetLayerBabylon({
    {% endif %}
            map,
            modelSource,
            modelOrigin,
            modelRotate,
            unitToMeter
        }));
    });
});