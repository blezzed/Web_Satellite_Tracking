Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwZjYzMjM2MS0wNTFlLTQwOWQtOGMyNC1mNDM4ZTY5MjQ0ZTEiLCJpZCI6MjIyMTYxLCJpYXQiOjE3MTgzNDQ3MjF9.KfrGuixYLYJ2cM-oyC_aTZaQ31b1lmF9yOCBWjyvXE0';

const viewer = new Cesium.Viewer("cesiumContainer", {
  shouldAnimate: true,
});

// Satellites button
const showSatellites = function () {
  // Load the satellite Two-Line Element (TLE) data
  const tle = `
1 25544U 98067A   23157.51785360  .00000730  00000-0  29512-4 0  9998
2 25544  51.6460  52.5440 0003722 317.1614  84.4617 15.49749866318531
`;

  // Create a satellite entity using SatelliteEntityWrapper
  const satEntity = new Cesium.SatelliteEntityWrapper({
    name: 'ISS',
    tle: tle
  });
  viewer.entities.add(satEntity.entity);

  // Add the satellite's path
  satEntity.path.show = true;
  satEntity.path.width = 2;
  satEntity.path.leadTime = 86400; // Show the path for the next 24 hours
  satEntity.path.trailTime = 86400; // Show the path for the previous 24 hours

  // Set the camera to follow the satellite
  viewer.trackedEntity = satEntity.entity;
  viewer.camera.setView({
    destination: satEntity.entity.position.getValue(Cesium.JulianDate.now()),
    orientation: {
      heading: Cesium.Math.toRadians(0.0),
      pitch: Cesium.Math.toRadians(-90.0),
      roll: 0.0
    }
  });

  // Update the satellite position every frame
  const clock = viewer.clock;
  clock.shouldAnimate = true;
  clock.multiplier = 1; // Set the playback speed (1 = real-time)

  function updateSatellitePosition() {
    const currentTime = clock.currentTime;
    satEntity.updatePositionAndOrientation(currentTime);
    requestAnimationFrame(updateSatellitePosition);
  }

  updateSatellitePosition();
};

// Vehicle button
const showVehicle = function () {
  viewer.dataSources.add(
    Cesium.CzmlDataSource.load("../SampleData/Vehicle.czml")
  );

  viewer.scene.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(-116.52, 35.02, 95000),
    orientation: {
      heading: 6,
    },
  });
};

// Reset button
const resetView = function () {
  viewer.dataSources.removeAll();
  viewer.entities.removeAll();
};

// Add buttons to the toolbar
const toolbar = document.createElement('div');
toolbar.style.position = 'absolute';
toolbar.style.top = '10px';
toolbar.style.left = '10px';
toolbar.style.zIndex = '999';


viewer.container.appendChild(toolbar);