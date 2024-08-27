from flask import Flask, render_template, jsonify
import random
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# 일본의 Level 1(지방) 및 Level 2(도시) GeoJSON 파일 경로
japan_level1_geojson_path = "C:/Users/a4651/Desktop/일본여행/japan-travel-/gadm41_JPN_1.json"  # 지방 경계
japan_level2_geojson_path = "C:/Users/a4651/Desktop/일본여행/japan-travel-/gadm41_JPN_2.json"  # 도시 경계

# GeoJSON 파일 불러오기
japan_level1_gdf = gpd.read_file(japan_level1_geojson_path)
japan_level2_gdf = gpd.read_file(japan_level2_geojson_path)

def generate_random_point_within_japan(gdf):
    polygon = gdf.geometry.unary_union  # 일본의 모든 폴리곤을 하나로 합침
    minx, miny, maxx, maxy = polygon.bounds
    
    while True:
        random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(random_point):
            return random_point

def find_region_and_city(point, level1_gdf, level2_gdf):
    region = None
    city = None

    for _, row in level1_gdf.iterrows():
        if row['geometry'].contains(point):
            region = row['NAME_1']  # 지방 이름 컬럼

    for _, row in level2_gdf.iterrows():
        if row['geometry'].contains(point):
            city = row['NAME_2']  # 도시 이름 컬럼

    return region, city

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    random_point = generate_random_point_within_japan(japan_level1_gdf)
    region, city = find_region_and_city(random_point, japan_level1_gdf, japan_level2_gdf)

    # 지도 생성
    fig, ax = plt.subplots()
    japan_level1_gdf.plot(ax=ax, color='lightblue')
    ax.plot(random_point.x, random_point.y, 'ro', markersize=5)

    # 이미지 버퍼로 저장
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # 결과 반환
    return jsonify({
        'image': img_base64,
        'region': region,
        'city': city,
    })

if __name__ == '__main__':
    app.run(debug=True)
