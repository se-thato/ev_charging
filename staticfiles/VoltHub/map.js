function initMap() {
  console.log("Initializing map...");

  const mapEl = document.getElementById("map");
  if (!mapEl) { console.error("Map element not found."); return; }

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

  // Separate marker stores so we can update/clear independently
  const ocmMarkers = [];
  const ourMarkers = {};  // keyed by station id for live updates

  let userPosition = null;

  //Marker icon definitions

  function getOurMarkerIcon(station) {
    // Green = 3+ slots, Amber = 1-2 slots, Red = full or offline
    const color = station.available_slots > 2 ? '#45ffbc'
                : station.available_slots > 0  ? '#ffc107'
                : '#ff4444';
    return {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 10,
      fillColor: color,
      fillOpacity: 1,
      strokeColor: '#ffffff',
      strokeWeight: 2,
    };
  }

  function getOcmMarkerIcon(status) {
    const colorMap = {
      online:  'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
      partial: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
      offline: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
      unknown: 'https://maps.google.com/mapfiles/ms/icons/ltblue-dot.png',
    };
    return { url: colorMap[status] || colorMap.unknown };
  }

  //Clear OCM markers
  function clearOcmMarkers() {
    ocmMarkers.forEach(m => m.setMap(null));
    ocmMarkers.length = 0;
  }

  //Directions
  function getDirections(destination) {
    const origin = userPosition || map.getCenter();
    directionsService.route(
      { origin, destination, travelMode: google.maps.TravelMode.DRIVING },
      (response, status) => {
        if (status === 'OK') {
          directionsRenderer.setDirections(response);
        } else {
          alert('Directions failed: ' + status);
        }
      }
    );
  }


  window.getDirectionsToStation = function(lat, lng) {
    getDirections({ lat, lng });
  };

  
  function buildOurInfoHtml(s) {
    const slots = `${s.available_slots}/${s.total_slots} slots`;
    const price = s.price_per_hour ? `R${s.price_per_hour}/hr` : 'Price N/A';
    const bookBtn = s.bookable
      ? `<a href="/book/?station_id=${s.id}" style="display:block;margin-top:.5rem;padding:.35rem .6rem;background:linear-gradient(90deg,#7a7cff,#00e5ff);color:#000;border-radius:8px;text-decoration:none;text-align:center;font-weight:700">Book Now</a>`
      : `<div style="margin-top:.5rem;color:#a9b1ff;font-size:.8rem">Not yet bookable</div>`;
    return `
      <div style="min-width:220px;font-family:sans-serif">
        <h5 style="margin:0 0 .25rem;color:#7a7cff">⚡ ${s.name}</h5>
        <p style="margin:0 0 .2rem;font-size:.85rem">${s.address || ''}</p>
        <p style="margin:0 0 .2rem;font-size:.85rem">${slots} · ${price}</p>
        <p style="margin:0 0 .4rem;font-size:.8rem;color:${s.status === 'online' ? '#45ffbc' : '#ff7b88'}">${s.status.toUpperCase()}</p>
        <button onclick="getDirectionsToStation(${s.lat}, ${s.lng})" style="padding:.3rem .6rem;background:rgba(0,229,255,.15);border:1px solid rgba(0,229,255,.4);color:#00e5ff;border-radius:8px;cursor:pointer">Get Directions</button>
        ${bookBtn}
      </div>`;
  }

  function buildOcmInfoHtml(s) {
    const connectors = s.connector_types && s.connector_types.length
      ? s.connector_types.join(', ')
      : 'Unknown';
    return `
      <div style="min-width:220px;font-family:sans-serif">
        <h5 style="margin:0 0 .25rem">${s.name}</h5>
        <p style="margin:0 0 .2rem;font-size:.85rem">${s.address || ''}</p>
        <p style="margin:0 0 .2rem;font-size:.85rem">Cost: ${s.usage_cost || 'N/A'}</p>
        <p style="margin:0 0 .2rem;font-size:.8rem">Connectors: ${connectors}</p>
        <p style="margin:0 0 .4rem;font-size:.8rem;color:${s.status === 'online' ? '#45ffbc' : '#888'}">
          ${s.status.toUpperCase()} · ${s.num_points || '?'} points
        </p>
        <button onclick="getDirectionsToStation(${s.lat}, ${s.lng})" style="padding:.3rem .6rem;background:rgba(0,229,255,.15);border:1px solid rgba(0,229,255,.4);color:#00e5ff;border-radius:8px;cursor:pointer">Get Directions</button>
      </div>`;
  }

  //Place VoltHub markers (with live updates)

  function placeOurMarker(s) {
    if (ourMarkers[s.id]) {
      ourMarkers[s.id].marker.setMap(null);
    }

    const marker = new google.maps.Marker({
      position: { lat: s.lat, lng: s.lng },
      map,
      title: s.name,
      icon: getOurMarkerIcon(s),
      zIndex: 10,  // always above OCM markers
    });

    const infoWindow = new google.maps.InfoWindow({ content: buildOurInfoHtml(s) });
    marker.addListener('click', () => infoWindow.open(map, marker));

    ourMarkers[s.id] = { marker, infoWindow, data: s };
  }

  // Placing OCM markers
  function placeOcmMarkers(stations) {
    clearOcmMarkers();
    stations.forEach(s => {
      if (!s.lat || !s.lng) return;
      const marker = new google.maps.Marker({
        position: { lat: s.lat, lng: s.lng },
        map,
        title: s.name,
        icon: getOcmMarkerIcon(s.status),
        zIndex: 1,
      });
      const infoWindow = new google.maps.InfoWindow({ content: buildOcmInfoHtml(s) });
      marker.addListener('click', () => infoWindow.open(map, marker));
      ocmMarkers.push(marker);
    });
  }

  
  function updateOurSidebar(stations) {
    // Use template-defined renderer if available (has styled cards + count badge)
    if (typeof window.renderOurSidebar === 'function') {
      window.renderOurSidebar(stations);
      return;
    }

    // Inline fallback
    const el = document.getElementById('our-stations-list');
    if (!el) return;
    if (!stations || stations.length === 0) {
      el.innerHTML = '<p style="color:var(--vh-muted);font-size:.85rem;padding:.5rem 0">No VoltHub stations nearby.</p>';
      return;
    }
    el.innerHTML = stations.map(s => {
      const slotColor = s.available_slots > 2 ? '#45ffbc'
                      : s.available_slots > 0  ? '#ffc107'
                      : '#ff4444';
      return `
        <div onclick="focusStation(${s.id}, 'volthub')" style="cursor:pointer;padding:.75rem;margin-bottom:.5rem;border-radius:10px;border:1px solid var(--vh-border);background:rgba(255,255,255,0.05)">
          <div style="font-weight:700;font-size:.88rem;color:var(--vh-text)">
            <span style="width:8px;height:8px;border-radius:50%;background:${slotColor};display:inline-block;margin-right:.4rem"></span>
            ${s.name}
          </div>
          <div style="font-size:.78rem;color:var(--vh-muted)">${s.address || ''}</div>
          <div style="font-size:.78rem;margin-top:.3rem;color:${slotColor}">${s.available_slots}/${s.total_slots} slots · ${s.status}</div>
          ${s.price_per_hour ? `<div style="font-size:.75rem;color:var(--vh-muted)">R${s.price_per_hour}/hr</div>` : ''}
        </div>`;
    }).join('');
  }

  function updateOcmSidebar(stations) {
    // Use template-defined renderer if available
    if (typeof window.renderOcmSidebar === 'function') {
      window.renderOcmSidebar(stations);
      return;
    }

    // Inline fallback
    const el = document.getElementById('ocm-stations-list');
    if (!el) return;
    if (!stations || stations.length === 0) {
      el.innerHTML = '<p style="color:var(--vh-muted);font-size:.85rem;padding:.5rem 0">No external stations found nearby.</p>';
      return;
    }
    el.innerHTML = stations.slice(0, 20).map(s => {
      const dotColor = s.status === 'online'  ? '#45ffbc'
                     : s.status === 'partial' ? '#ffc107'
                     : '#ff4444';
      return `
        <div style="padding:.65rem;margin-bottom:.5rem;border-radius:10px;border:1px solid var(--vh-border);background:rgba(255,255,255,0.03)">
          <div style="font-weight:600;font-size:.85rem;color:var(--vh-text)">
            <span style="width:8px;height:8px;border-radius:50%;background:${dotColor};display:inline-block;margin-right:.4rem"></span>
            ${s.name}
          </div>
          <div style="font-size:.75rem;color:var(--vh-muted)">${s.address || ''}</div>
          <div style="font-size:.75rem;margin-top:.25rem;color:var(--vh-muted)">${s.connector_types ? s.connector_types.slice(0, 2).join(', ') : ''} · ${s.num_points || '?'} points</div>
        </div>`;
    }).join('');
  }

  // Focus map on a station and open its info window
  window.focusStation = function(stationId, source) {
    if (source === 'volthub' && ourMarkers[stationId]) {
      const { marker, infoWindow } = ourMarkers[stationId];
      map.panTo(marker.getPosition());
      map.setZoom(15);
      infoWindow.open(map, marker);
    }
  };

  // Fetching both station types from Django proxy

  function fetchStations(center) {
    const lat = typeof center.lat === 'function' ? center.lat() : center.lat;
    const lng = typeof center.lng === 'function' ? center.lng() : center.lng;

    console.log('Fetching stations via Django proxy for:', lat, lng);

    const ourList = document.getElementById('our-stations-list');
    const ocmList = document.getElementById('ocm-stations-list');
    if (ourList && !wsConnected) ourList.innerHTML = '<p style="color:var(--vh-muted);font-size:.85rem">Loading...</p>';
    if (ocmList) ocmList.innerHTML = '<p style="color:var(--vh-muted);font-size:.85rem">Loading...</p>';

    fetch(`/api/stations/nearby/?lat=${lat}&lng=${lng}`)
      .then(r => {
        if (!r.ok) throw new Error('API error ' + r.status);
        return r.json();
      })
      .then(data => {
        // OCM markers and right sidebar always come from REST
        placeOcmMarkers(data.ocm_stations || []);
        updateOcmSidebar(data.ocm_stations || []);

        // Our stations come from WebSocket (live)
        // Only use REST fallback if WebSocket is not connected
        if (!wsConnected && data.our_stations) {
          data.our_stations.forEach(placeOurMarker);
          updateOurSidebar(data.our_stations);
        }
      })
      .catch(err => {
        console.error('Station fetch error:', err);
        if (ocmList) ocmList.innerHTML = '<p style="color:#ff7b88;font-size:.85rem">Failed to load stations.</p>';
      });
  }

  //WebSocket for live VoltHub station updates

  let wsConnected = false;
  let wsReconnectTimer = null;

  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stations/`;

    console.log('Connecting WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Station WebSocket connected');
      wsConnected = true;
      clearTimeout(wsReconnectTimer);
      // Update the connection indicator in the map corner
      if (typeof window.setWsStatus === 'function') window.setWsStatus(true);
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'snapshot') {
        // Initial full load — placing all VoltHub stations at once
        msg.stations.forEach(placeOurMarker);
        updateOurSidebar(msg.stations);

      } else if (msg.type === 'station_update') {
        // Single station changed, update just that one marker + sidebar
        const s = msg.station;
        placeOurMarker(s);

        // building full sidebar with updated data
        const allStations = Object.values(ourMarkers).map(m => m.data);
        const idx = allStations.findIndex(d => d.id === s.id);
        if (idx !== -1) allStations[idx] = s;
        updateOurSidebar(allStations);
      }
    };

    ws.onclose = () => {
      console.warn('Station WebSocket closed. Reconnecting in 5s...');
      wsConnected = false;
      // Update the connection indicator
      if (typeof window.setWsStatus === 'function') window.setWsStatus(false);
      // Auto-reconnect after 5 seconds
      wsReconnectTimer = setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      ws.close();
    };

    // Keepalive ping every 30 seconds to prevent proxy timeout
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  // Start WebSocket connection immediately
  connectWebSocket();

  //Search autocomplete

  const input = document.getElementById('search-input');
  if (input) {
    const autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', map);
    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      if (!place || !place.geometry) return;
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
      } else {
        map.setCenter(place.geometry.location);
        map.setZoom(14);
      }
      fetchStations(place.geometry.location);
    });
  }

  // Re-fetch OCM stations when map stops moving
  // Using 'idle' event with a short debounce to avoid hammering the API
  let mapMoveTimer = null;
  map.addListener('idle', () => {
    clearTimeout(mapMoveTimer);
    mapMoveTimer = setTimeout(() => {
      fetchStations(map.getCenter());
    }, 800);
  });

  //Geolocation

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userPosition = { lat: position.coords.latitude, lng: position.coords.longitude };

        new google.maps.Marker({
          position: userPosition,
          map,
          title: 'Your Location',
          icon: { url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png' },
          animation: google.maps.Animation.DROP,
          zIndex: 20,
        });

        map.setCenter(userPosition);
        map.setZoom(13);
        fetchStations(userPosition);
      },
      (error) => {
        console.warn('Geolocation failed:', error);
        fetchStations(map.getCenter());
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 300000 }
    );
  } else {
    fetchStations(map.getCenter());
  }
}