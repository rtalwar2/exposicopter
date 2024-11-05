// https://github.com/Leaflet/Leaflet.heat?tab=readme-ov-file

let map = L.map('map').setView([50.8257352145159, 3.26680419429943],14);
map.options.maxZoom = 50;  // Allow zooming up to level 22

let data_shown=false;
let heatmapLayer;
let existingData = [];

function init_map(){
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 50,
        // maxNativeZoom: 50,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        
    }).addTo(map);
    heatmapLayer = L.heatLayer([], {
        radius: 15,        // controls the size of each “heat” point
        blur: 15,          // blur factor to smooth the heatmap
        maxZoom: 25,       // max zoom level for the heatmap
        max: 1.0           // maximum intensity
    }).addTo(map);
}

// // Function to interpolate points between two coordinates
// function interpolatePoints(start, end, numPoints) {
//     const points = [];
//     for (let i = 0; i <= numPoints; i++) {
//         const fraction = i / numPoints;
//         const lat = start.lat + fraction * (end.lat - start.lat);
//         const lon = start.lon + fraction * (end.lon - start.lon);
//         const value = start.value + fraction * (end.value - start.value);
//         points.push({ lat, lon, value });
//     }
//     return points;
// }

function showData(data){
    if (!data_shown){
        const firstDataPoint = data[0];
        map.flyTo([firstDataPoint.lat, firstDataPoint.lon], 19, {
            animate: true,          // Enable animation
            duration: 2              // Duration of flyTo animation in seconds
        });
        data_shown=true;
    }

    let newData = data.filter(point => {
        return !existingData.some(shownPoint =>
            shownPoint.lat === point.lat && shownPoint.lon === point.lon && shownPoint.value === point.value
        );
    });
    console.log(newData)
    // Add new data points to the heatmap
    // Interpolate between points and add each interpolated point individually to the heatmap layer
    // newData.forEach((point, index) => {
    //     if (index > 0) {
    //         // Get the previous point
    //         const prevPoint = newData[index - 1];
    //         // Interpolate between prevPoint and current point
    //         const interpolatedPoints = interpolatePoints(prevPoint, point, 5);  // 5 interpolated points between each pair
    //         interpolatedPoints.forEach(interpolatedPoint => {
    //             heatmapLayer.addLatLng([interpolatedPoint.lat, interpolatedPoint.lon, interpolatedPoint.value]);
    //             existingData.push(interpolatedPoint);
    //         });
    //     }

    //     // Add the current point
    //     heatmapLayer.addLatLng([point.lat, point.lon, point.value]);
    //     existingData.push(point);  // Add to the existing data tracker
    // });

    // Add each new data point individually to the heatmap layer
    newData.forEach(point => {
        heatmapLayer.addLatLng([point.lat, point.lon, point.value]);
        existingData.push(point);  // Add to the existing data tracker
    });

}

function loadData(){
    const url = "http://127.0.0.1:8000/sensor_data"
    fetch(url, {
        method: 'GET'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // console.log("this is the data", data);
            showData(data);
        })
        .catch(error => {
            // Handle error
            console.error('There was a problem with the retrieval of the data:', error);
        });
}

function main() {
    init_map();
    setInterval(()=>{setTimeout(loadData,1)}, 2000);
}

main()