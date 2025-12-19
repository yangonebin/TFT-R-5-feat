<template>
  <div class="map-layout">
    <aside class="sidebar">
      <h2 class="sidebar-title">은행 찾기</h2>
      
      <div class="filter-group">
        <label>광역시/도</label>
        <select v-model="province" @change="updateDistrict">
          <option value="">전체</option>
          <option value="서울">서울</option>
          <option value="경기">경기</option>
          <option value="부산">부산</option>
          <option value="대구">대구</option>
          <option value="인천">인천</option>
          <option value="광주">광주</option>
          <option value="대전">대전</option>
          <option value="울산">울산</option>
        </select>
      </div>

      <div class="filter-group">
        <label>시/군/구</label>
        <input type="text" v-model="district" placeholder="예: 강남구, 해운대구">
      </div>

      <div class="filter-group">
        <label>은행</label>
        <select v-model="bankName">
          <option value="은행">전체</option>
          <option value="국민은행">국민은행</option>
          <option value="신한은행">신한은행</option>
          <option value="우리은행">우리은행</option>
          <option value="하나은행">하나은행</option>
          <option value="농협은행">농협은행</option>
          <option value="기업은행">기업은행</option>
        </select>
      </div>

      <button class="search-btn" @click="searchPlaces">찾기</button>

      <div class="result-msg" v-if="searchMsg">
        {{ searchMsg }}
      </div>

      <div class="selected-info" v-if="selectedPlace">
        <h4>{{ selectedPlace.place_name }}</h4>
        <p class="addr">{{ selectedPlace.address_name }}</p>
        <p class="phone">{{ selectedPlace.phone }}</p>
        <div class="route-info" v-if="routeDistance">
          <strong>거리:</strong> {{ (routeDistance / 1000).toFixed(1) }}km
          <br>
          <strong>예상 시간:</strong> {{ Math.round(routeDuration / 60) }}분
        </div>
      </div>
    </aside>

    <div id="kakao-map" class="map-area"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'

// 1. 상태 변수
const map = ref(null)
const markers = ref([])
const infoWindow = ref(null)
const polyline = ref(null)

// 검색 필터 변수
const province = ref('서울')
const district = ref('강남구')
const bankName = ref('국민은행')

// UI 상태
const searchMsg = ref('')
const selectedPlace = ref(null)
const routeDistance = ref(0)
const routeDuration = ref(0)

// 상수: 멀티캠퍼스 역삼 (출발지)
const START_LOC = {
  lat: 37.5012743,
  lng: 127.039585
}

// 2. 지도 초기화
onMounted(() => {
  if (window.kakao && window.kakao.maps) {
    initMap()
  } else {
    const script = document.createElement('script')
    script.onload = () => kakao.maps.load(initMap)
    script.src = '//dapi.kakao.com/v2/maps/sdk.js?appkey=30683db36325ba7dbe3f71aa5c16192a&autoload=false&libraries=services'
    document.head.appendChild(script)
  }
})

const initMap = () => {
  const container = document.getElementById('kakao-map')
  const options = {
    center: new kakao.maps.LatLng(START_LOC.lat, START_LOC.lng),
    level: 5
  }

  map.value = new kakao.maps.Map(container, options)
  infoWindow.value = new kakao.maps.InfoWindow({ zIndex: 1 })

  // 출발지(멀티캠퍼스) 마커 표시 (빨간색)
  const startImgSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png'
  const startImgSize = new kakao.maps.Size(35, 38)
  const startMarker = new kakao.maps.Marker({
    position: new kakao.maps.LatLng(START_LOC.lat, START_LOC.lng),
    image: new kakao.maps.MarkerImage(startImgSrc, startImgSize),
    map: map.value
  })

  // 인포윈도우로 출발지 표시
  const iwContent = '<div style="padding:5px;">멀티캠퍼스 (출발)</div>'
  const iw = new kakao.maps.InfoWindow({ position: startMarker.getPosition(), content: iwContent })
  iw.open(map.value, startMarker)
}

// 3. 통합 검색 기능
const searchPlaces = () => {
  // 검색어 조합 (예: 서울 강남구 국민은행)
  const keyword = `${province.value} ${district.value} ${bankName.value}`.trim()
  
  if (!keyword) {
    alert('검색 조건을 입력해주세요.')
    return
  }

  const ps = new kakao.maps.services.Places()
  
  // 키워드로 장소 검색
  ps.keywordSearch(keyword, (data, status, pagination) => {
    if (status === kakao.maps.services.Status.OK) {
      displayPlaces(data)
      searchMsg.value = `검색된 마커를 클릭하면 경로가 출력됩니다.`
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
      alert('검색 결과가 존재하지 않습니다.')
      searchMsg.value = ''
    } else {
      alert('검색 중 오류가 발생했습니다.')
    }
  })
}

// 4. 마커 표시 함수
const displayPlaces = (places) => {
  // 기존 마커 및 경로 제거
  removeMarkers()
  if (polyline.value) polyline.value.setMap(null)
  if (infoWindow.value) infoWindow.value.close()
  selectedPlace.value = null

  // 지도 범위 재설정용 bounds
  const bounds = new kakao.maps.LatLngBounds()

  for (let i = 0; i < places.length; i++) {
    const place = places[i]
    const placePosition = new kakao.maps.LatLng(place.y, place.x)
    
    // 마커 생성
    const marker = new kakao.maps.Marker({
      position: placePosition,
      map: map.value
    })

    // 마커 클릭 이벤트
    kakao.maps.event.addListener(marker, 'click', () => {
      displayInfoWindow(marker, place)
      getRoute(place) // 길찾기 실행
    })

    markers.value.push(marker)
    bounds.extend(placePosition)
  }

  // 검색된 장소들이 모두 보이도록 지도 범위 재설정
  map.value.setBounds(bounds)
}

const removeMarkers = () => {
  for (let i = 0; i < markers.value.length; i++) {
    markers.value[i].setMap(null)
  }
  markers.value = []
}

// 인포윈도우 표시
const displayInfoWindow = (marker, place) => {
  const content = `
    <div style="padding:10px; z-index:1; width:200px;">
      <h5 style="margin:0 0 5px; font-size:14px; color:#154580;">${place.place_name}</h5>
      <span style="font-size:12px; color:#666;">${place.address_name}</span>
    </div>
  `
  infoWindow.value.setContent(content)
  infoWindow.value.open(map.value, marker)
  selectedPlace.value = place
}

// 5. 길찾기 기능 (Kakao Mobility API)
const getRoute = async (destination) => {
  // REST API 키 적용
  const REST_API_KEY = '09105391afdc098b52f08fe152204bba'
  
  const origin = `${START_LOC.lng},${START_LOC.lat}` // 출발지 (경도,위도)
  const dest = `${destination.x},${destination.y}`   // 목적지 (경도,위도)

  try {
    const response = await axios.get('https://apis-navi.kakaomobility.com/v1/directions', {
      params: {
        origin: origin,
        destination: dest,
        priority: 'RECOMMEND'
      },
      headers: {
        Authorization: `KakaoAK ${REST_API_KEY}`,
        // 주의: 브라우저에서 직접 호출 시 CORS 에러 발생 가능성 있음
        // 에러 발생 시 백엔드 Proxy 구현 필요
      }
    })

    const routes = response.data.routes[0]
    
    // 거리 및 시간 정보 저장
    routeDistance.value = routes.summary.distance
    routeDuration.value = routes.summary.duration

    // 경로 그리기
    drawPolyline(routes)

  } catch (error) {
    console.error('Mobility API Error:', error)
    alert('경로를 가져올 수 없습니다. (CORS 보안 정책으로 인해 백엔드를 거쳐야 할 수 있습니다)')
  }
}

// 경로 그리기 (Polyline)
const drawPolyline = (routes) => {
  if (polyline.value) {
    polyline.value.setMap(null) // 기존 경로 삭제
  }

  const linePath = []
  
  routes.sections.forEach(section => {
    section.roads.forEach(road => {
      for (let i = 0; i < road.vertexes.length; i += 2) {
        linePath.push(new kakao.maps.LatLng(road.vertexes[i + 1], road.vertexes[i]))
      }
    })
  })

  polyline.value = new kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 7,
    strokeColor: '#FF3300', // 잘 보이는 주황색 계열
    strokeOpacity: 0.8,
    strokeStyle: 'solid'
  })

  polyline.value.setMap(map.value)
}
</script>

<style scoped>
.map-layout {
  display: flex;
  height: calc(100vh - 80px); /* 헤더 제외 높이 */
  width: 100%;
}

/* 사이드바 스타일 */
.sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #ddd;
  padding: 20px;
  overflow-y: auto;
  box-shadow: 2px 0 5px rgba(0,0,0,0.05);
  z-index: 10;
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #333;
}

.filter-group {
  margin-bottom: 15px;
}

.filter-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 5px;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.95rem;
}

.search-btn {
  width: 100%;
  padding: 12px;
  background-color: #e55039; /* 요청하신 주황/빨강 계열 */
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.2s;
}

.search-btn:hover {
  background-color: #c0392b;
}

.result-msg {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  color: #555;
  border-radius: 4px;
}

.selected-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border: 1px solid #3182f6;
  border-radius: 8px;
}

.selected-info h4 {
  margin: 0 0 5px 0;
  color: #154580;
}

.selected-info .addr {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 5px;
}

.route-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
  font-size: 0.9rem;
}

/* 지도 영역 스타일 */
.map-area {
  flex: 1; /* 남은 공간 모두 차지 */
  width: 100%;
  height: 100%;
}
</style>