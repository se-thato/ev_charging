function initMap() {
  console.log("Initializing map...");

  const mapEl = document.getElementById("map");
  if (!mapEl) {
    console.error("Map element with id 'map' not found.");
    return;
  }

  const map = new google.maps.Map(mapEl, {
    zoom: 12,
    center: { lat: -26.341069, lng: 28.132964 },
    mapTypeControl: false,
    streetViewControl: true,
    fullscreenControl: true,
  });

  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer({ suppressMarkers: true });
  directionsRenderer.setMap(map);

  const markers = [];

  function addMarker(position, title, type = "station") {
    const iconMap = {
      user: { url: "https://maps.google.com/mapfiles/ms/icons/green-dot.png" },
      place: { url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png" },
    };

    const marker = new google.maps.Marker({
      position,
      map,
      title,
      icon: iconMap[type] || undefined,
      animation: type === "user" ? google.maps.Animation.DROP : undefined,
    });
    markers.push(marker);
    return marker;
  }

  function calculateAndDisplayRoute(directionsService, directionsRenderer, origin, destination) {
    directionsService.route(
      {
        origin: origin,
        destination: destination,
        travelMode: google.maps.TravelMode.DRIVING,
      },
      function (response, status) {
        if (status === "OK") {
          directionsRenderer.setDirections(response);
        } else {
          window.alert("Directions request failed due to " + status);
        }
      }
    );
  }

  function toLatLng(center) {
    // Accepts either a google.maps.LatLng or {lat, lng}
    return {
      lat: typeof center.lat === "function" ? center.lat() : center.lat,
      lng: typeof center.lng === "function" ? center.lng() : center.lng,
    };
  }

  function fetchStations(center) {
    const { lat, lng } = toLatLng(center);
    const url = `https://api.openchargemap.io/v3/poi/?output=json&latitude=${lat}&longitude=${lng}&distance=25&distanceunit=KM&maxresults=100&key=59fb39de-df2a-492f-9409-f048cce0e051`;

    console.log("Fetching stations near:", lat, lng);

    return fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error("OpenChargeMap request failed: " + response.status);
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data) || data.length === 0) {
          console.warn("No charging stations found for the current area.");
          return;
        }

        data.forEach((station) => {
          if (!station || !station.AddressInfo) return;
          const pos = {
            lat: station.AddressInfo.Latitude,
            lng: station.AddressInfo.Longitude,
          };

          const marker = addMarker(pos, station.AddressInfo.Title, "station");

          const infoHtml = `
            <div style="min-width:220px">
              <h5 style="margin:0 0 .25rem">${station.AddressInfo.Title || "Charging Station"}</h5>
              <p style="margin:0 0 .25rem">${station.AddressInfo.AddressLine1 || ""}</p>
              <p style="margin:0 0 .5rem">Price: ${station.UsageCost || "N/A"}</p>
              <button id="dir-btn-${station.ID}" style="background:linear-gradient(180deg, rgba(0,229,255,0.18), rgba(122,124,255,0.12)); border:1px solid rgba(122,124,255,0.35); color:#0ff; padding:.35rem .6rem; border-radius:10px; cursor:pointer">Get Directions</button>
            </div>`;

          const infoWindow = new google.maps.InfoWindow({ content: infoHtml });

          marker.addListener("click", function () {
            infoWindow.open(map, marker);
            google.maps.event.addListenerOnce(infoWindow, "domready", function () {
              const btn = document.getElementById(`dir-btn-${station.ID}`);
              if (btn) {
                btn.onclick = function () {
                  const origin = userPosition || map.getCenter();
                  calculateAndDisplayRoute(
                    directionsService,
                    directionsRenderer,
                    origin,
                    marker.getPosition()
                  );
                };
              }
            });
          });
        });
      })
      .catch((err) => console.error("Error fetching stations:", err));
  }

  // Places Autocomplete for search
  const input = document.getElementById("search-input");
  if (input) {
    const autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo("bounds", map);
    autocomplete.addListener("place_changed", function () {
      const place = autocomplete.getPlace();
      if (!place || !place.geometry) {
        console.warn("Autocomplete returned place with no geometry.");
        return;
      }
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
      } else {
        map.setCenter(place.geometry.location);
        map.setZoom(14);
      }
      addMarker(place.geometry.location, place.name || "Selected place", "place");
      fetchStations(place.geometry.location);
    });
  } else {
    console.warn("Search input element not found. The Places search will be disabled.");
  }

  // Try to use Geolocation; fall back to map center if denied or unsupported
  let userPosition = null;
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        userPosition = { lat: position.coords.latitude, lng: position.coords.longitude };
        addMarker(userPosition, "Your Location", "user");
        map.setCenter(userPosition);
        map.setZoom(13);
        fetchStations(userPosition);
      },
      function (error) {
        console.warn("Geolocation failed or denied:", error);
        const fallback = map.getCenter();
        fetchStations(fallback);
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 300000 }
    );
  } else {
    console.warn("Geolocation not supported in this browser. Using map center.");
    fetchStations(map.getCenter());
  }
}
