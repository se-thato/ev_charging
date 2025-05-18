function initMap() {
    console.log("Initializing map..."); // Debugging log to ensure the function is called

    var map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: { lat: -26.341069, lng: 28.132964 }
    });

    var input = document.getElementById('search-input');
    if (!input) {
        console.error("Search input element not found. Ensure the element with id 'search-input' exists in the HTML.");
        return;
    }

    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', map);

    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            console.error("Autocomplete returned place with no geometry.");
            return;
        }

        var bounds = new google.maps.LatLngBounds();
        if (place.geometry.viewport) {
            bounds.union(place.geometry.viewport);
        } else {
            bounds.extend(place.geometry.location);
        }
        map.fitBounds(bounds);

        new google.maps.Marker({
            map: map,
            title: place.name,
            position: place.geometry.location
        });
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            var currentLocationMarker = new google.maps.Marker({
                position: pos,
                map: map,
                title: "Your Location",
                icon: {
                    url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
                },
                animation: google.maps.Animation.BOUNCE
            });

            map.setCenter(pos);

            fetch(`https://api.openchargemap.io/v3/poi/?output=json&latitude=${pos.lat}&longitude=${pos.lng}&distance=10&distanceunit=KM&key=59fb39de-df2a-492f-9409-f048cce0e051`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.length === 0) {
                        console.warn('No charging stations found.');
                    }
                    data.forEach(station => {
                        var marker = new google.maps.Marker({
                            position: { lat: station.AddressInfo.Latitude, lng: station.AddressInfo.Longitude },
                            map: map,
                            title: station.AddressInfo.Title
                        });

                        var infoWindow = new google.maps.InfoWindow({
                            content: `<h5>${station.AddressInfo.Title}</h5>
                                      <p>${station.AddressInfo.AddressLine1}</p>
                                      <p>Price: ${station.UsageCost || 'N/A'}</p>`
                        });

                        marker.addListener('click', function() {
                            infoWindow.open(map, marker);
                        });
                    });
                })
                .catch(error => console.error('Error fetching data:', error));
        }, function() {
            handleLocationError(true, map.getCenter());
        });
    } else {
        handleLocationError(false, map.getCenter());
    }

    function handleLocationError(browserHasGeolocation, pos) {
        var infoWindow = new google.maps.InfoWindow({
            map: map,
            position: pos,
            content: browserHasGeolocation ?
                'Error: The Geolocation service failed.' :
                'Error: Your browser doesn\'t support geolocation.'
        });
        infoWindow.open(map);
    }
}

