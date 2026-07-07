require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/GeoJSONLayer",
    "esri/widgets/LayerList",
    "esri/widgets/Legend"
], function (Map, MapView, GeoJSONLayer, LayerList, Legend) {

    // Expressão Arcade compartilhada entre as camadas de ponto: monta uma
    // lista só com os veículos que de fato participaram da colisão
    // (campo == "YES"), ao invés de mostrar YES/NO para todos os campos.
    const vehicleExpression = {
        name: "vehiclesInvolved",
        title: "Vehicles Involved",
        expression: `
            var vehicles = [];
            if ($feature.AUTOMOBILE == "YES") { Push(vehicles, "Automobile") }
            if ($feature.MOTORCYCLE == "YES") { Push(vehicles, "Motorcycle") }
            if ($feature.PASSENGER == "YES") { Push(vehicles, "Passenger") }
            if ($feature.BICYCLE == "YES") { Push(vehicles, "Bicycle") }
            if ($feature.PEDESTRIAN == "YES") { Push(vehicles, "Pedestrian") }
            if (Count(vehicles) == 0) { return "Not specified" }
            return Concatenate(vehicles, ", ")
        `
    };

    // fieldInfos compartilhado, para formatar OCC_DATE como data legível
    // em vez de timestamp Unix cru
    const dateFieldInfo = [
        { fieldName: "OCC_DATE", format: { dateFormat: "short-date" } }
    ];

    const signalsLayer = new GeoJSONLayer({
        url: "./data/collisions_near_signals.geojson",
        title: "Collisions x Signals (50m)",
        renderer: {
            type: "simple",
            symbol: {
                type: "picture-marker",
                url: "./assets/icons/traffic-light.svg",
                width: "10px",
                height: "18px"
            }
        },
        popupTemplate: {
            title: "Collisions near traffic light",
            content: "Date: {OCC_DATE}<br>Injury collision: {INJURY_COLLISIONS}<br>Vehicles involved: {expression/vehiclesInvolved}",
            expressionInfos: [vehicleExpression],
            fieldInfos: dateFieldInfo
        },
        visible: true
    });

    const bikeLanesLayer = new GeoJSONLayer({
        url: "./data/collisions_near_bike_lanes.geojson",
        title: "Collisions x Bike Lanes (25m)",
        renderer: {
            type: "simple",
            symbol: {
                type: "picture-marker",
                url: "./assets/icons/bike.svg",
                width: "26px",
                height: "16px"
            }
        },
        popupTemplate: {
            title: "Collisions near bike lane",
            content: "Date: {OCC_DATE}<br>Injury collision: {INJURY_COLLISIONS}<br>Vehicles involved: {expression/vehiclesInvolved}",
            expressionInfos: [vehicleExpression],
            fieldInfos: dateFieldInfo
        },
        visible: false
    });

    const neighbourhoodsLayer = new GeoJSONLayer({
        url: "./data/collisions_by_neighbourhood.geojson",
        title: "Collisions by Neighbourhood",
        renderer: {
            type: "simple",
            symbol: {
                type: "picture-marker",
                url: "./assets/icons/pin.svg",
                width: "14px",
                height: "19px"
            }
        },
        popupTemplate: {
            title: "{AREA_NAME}",
            content: "Date of collision: {OCC_DATE}<br>Injury collision: {INJURY_COLLISIONS}<br>Vehicles involved: {expression/vehiclesInvolved}",
            expressionInfos: [vehicleExpression],
            fieldInfos: dateFieldInfo
        },
        visible: false
    });

    const schoolsLayer = new GeoJSONLayer({
        url: "./data/collisions_near_schools.geojson",
        title: "Collisions x Schools (150m)",
        renderer: {
            type: "simple",
            symbol: {
                type: "picture-marker",
                url: "./assets/icons/school.svg",
                width: "18px",
                height: "18px"
            }
        },
        popupTemplate: {
            title: "Collisions near school",
            content: "Date: {OCC_DATE}<br>Injury collision: {INJURY_COLLISIONS}<br>Vehicles involved: {expression/vehiclesInvolved}",
            expressionInfos: [vehicleExpression],
            fieldInfos: dateFieldInfo
        },
        visible: false
    });

    const neighbourhoodsChoropleth = new GeoJSONLayer({
        url: "./data/neighbourhoods_with_counts.geojson",
        title: "Collisions Density by Neighbourhood",
        renderer: {
            type: "class-breaks",
            field: "COLLISION_COUNT",
            classBreakInfos: [
                { minValue: 0, maxValue: 315, symbol: { type: "simple-fill", color: [255, 243, 176, 0.6], outline: { color: "#999", width: 0.5 } } },
                { minValue: 315.01, maxValue: 425.8, symbol: { type: "simple-fill", color: [255, 204, 102, 0.6], outline: { color: "#999", width: 0.5 } } },
                { minValue: 425.81, maxValue: 591.2, symbol: { type: "simple-fill", color: [255, 153, 51, 0.6], outline: { color: "#999", width: 0.5 } } },
                { minValue: 591.21, maxValue: 896.0, symbol: { type: "simple-fill", color: [230, 74, 25, 0.6], outline: { color: "#999", width: 0.5 } } },
                { minValue: 896.01, maxValue: 3220, symbol: { type: "simple-fill", color: [183, 28, 28, 0.6], outline: { color: "#999", width: 0.5 } } }
            ]
        },
        popupTemplate: {
            title: "{AREA_NAME}",
            content: "Total collisions (last 2 years): {COLLISION_COUNT}"
        },
        visible: false
    });

    const fatalCollisionsLayer = new GeoJSONLayer({
        url: "./data/collisions_with_fatalities.geojson",
        title: "⚠️ Fatal Collisions",
        renderer: {
            type: "simple",
            symbol: {
                type: "simple-marker",
                style: "diamond",
                color: [139, 0, 0, 0.9],
                size: 14,
                outline: { color: "white", width: 1.5 }
            }
        },
        popupTemplate: {
            title: "Fatal Collision",
            content: "Date: {OCC_DATE}<br>Fatalities: {FATALITIES}<br>Vehicles involved: {expression/vehiclesInvolved}",
            expressionInfos: [vehicleExpression],
            fieldInfos: dateFieldInfo
        },
        visible: false
    });

    const map = new Map({
        basemap: "osm",
        layers: [neighbourhoodsChoropleth, signalsLayer, bikeLanesLayer, neighbourhoodsLayer, schoolsLayer, fatalCollisionsLayer]
    });

    const view = new MapView({
        container: "viewDiv",
        map: map,
        center: [-79.38, 43.70],
        zoom: 11
    });

    const layerList = new LayerList({ view: view });
    view.ui.add(layerList, "top-right");

    const legend = new Legend({ view: view });
    view.ui.add(legend, "bottom-left");
});
