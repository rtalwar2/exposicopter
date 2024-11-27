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

function onFileChange(event){
    const file = event.target.files[0]; 
    // setting up the reader
    const  reader = new FileReader();
    reader.readAsText(file,'UTF-8');
    // here we tell the reader what to do when it's done reading...
    reader.onload = readerEvent => {
        const content = readerEvent.target.result;
        // Split the CSV content into rows
        const rows = content.split('\n').filter(row => row.trim() !== '');
        // Remove the header row (first row)
        rows.shift();
        // Map each row to a JSON object
        const data = rows.map(row => {
            const [lat, lon, value] = row.split(',').map(item => item.trim());
            return {
                lat: parseFloat(lat),
                lon: parseFloat(lon),
                value: parseFloat(value)
            };
        });
        console.log(data); // Array of JSON objects
        showPlotlyData(data);
        showMapData(data);
    }
}


function postLocationforInspection(point){
    const url = "http://127.0.0.1:8000/inspect"
    fetch(url, {
        method: 'POST',
        body : point
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("this is the data", data);
            showPlotlyData(data);
            showMapData(data);
        })
        .catch(error => {
            // Handle error
            console.error('There was a problem with the retrieval of the data:', error);
        });
}

function showPlotlyData(data){
    Plotly.newPlot('heatmap', [{
        x: data.map(d => d.lon),
        y: data.map(d => d.lat),
        mode: 'markers',
        type: 'scatter',
        marker: {
            color: data.map(d => d.value),  // Color points based on their value
            colorscale: 'Jet',              // Use a color scale for heatmap effect
            showscale: true                     // Show the color scale legend
        },
        text: data.map(d => `Value: ${d.value}`)
    }], {
        title: 'Heatmap of Measurements',
        xaxis: {
            scaleanchor: 'y',    // Lock aspect ratio to y-axis
            scaleratio: 1,        // Ensure 1:1 ratio with the y-axis
            showline: false,
            showgrid: false,
            zeroline: false,
        },
        yaxis: {
            scaleanchor: 'x',    // Lock aspect ratio to x-axis
            scaleratio: 1,        // Ensure 1:1 ratio with the x-axis
            showline: false,
            showgrid: false,
            zeroline: false,
        }
    });
    if(!data_shown){
        document.querySelector("#heatmap").on('plotly_click', function(data){
            const pt = data.points[0]
            console.log(pt.x ,pt.y )
            postLocationforInspection({"lat": pt.y,"lon": pt.x})
        });
    }
}

function showMapData(data){
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
    // Add each new data point individually to the heatmap layer
    newData.forEach(point => {
        heatmapLayer.addLatLng([point.lat, point.lon, point.value]);
        existingData.push(point);  // Add to the existing data tracker
    });

}



function selectFile(){
    document.querySelector("#fileSelector").click()
}

function main() {
    init_map();
    // setInterval(()=>{setTimeout(loadData,1)}, 2000);
    // console.log(kaas)
    document.querySelector("#fileSelectorBtn").addEventListener("click",selectFile)
    document.querySelector("#fileSelector").addEventListener("change",onFileChange)

}

main()