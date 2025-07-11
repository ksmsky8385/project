// CSV 데이터 처리 및 차트 생성 스크립트
// 파일명: script_chartpage_csv_handler.js

// 전역 변수
let csvData = null;
let currentChart = null;
let chartData = null;

// 차트 색상 팔레트
const CHART_COLORS = [
    '#42a5f5', '#29b6f6', '#1e88e5', '#1976d2', '#1565c0',
    '#0d47a1', '#81c784', '#66bb6a', '#4caf50', '#43a047',
    '#388e3c', '#2e7d32', '#ffb74d', '#ffa726', '#ff9800',
    '#fb8c00', '#f57c00', '#ef6c00', '#ff8a65', '#ff7043'
];

// 피처별 한글명 매핑
const FEATURE_NAMES = {
    'SCR': '점수',
    'SNM': '학교명',
    'YR': '연도',
    'APS_APS': '재학생 1인당 도서관건물 연면적',
    'BGT_MCT': '예산_자료구입비계',
    'BGT_UBGT': '예산_대학총예산',
    'BPS_BPS': '재학생 1인당 소장도서수',
    'BR_BCNT_SUM': '도서자료_책수_계',
    'CPSS_CPS': '재학생 1인당 자료구입비(결산)',
    'EHS_EHS': '직원 1인당 평균 교육 참여 시간',
    'FACLT_EQP_TPC': '시설설비정보화기기(PC)수',
    'FACLT_LAS': '시설_도서관건물연면적',
    'FACLT_RS_TRS': '시설_열람석_총열람석수',
    'LBRT_USTL': '대학총결산 대비 도서관 자료구입비 비율',
    'LPK_LPK': '재학생 1,000명당 사서 직원수',
    'LPS_LPS': '재학생 1인당 대출책수',
    'LS_LB_SUM': '대출현황_대출책수_계',
    'LS_LU_SUM': '대출현황_대출자수_계',
    'SPK_SPK': '재학생 1,000명당 도서관 직원수',
    'STL_MCT': '결산_자료구입비계',
    'STL_USTL': '결산_대학총결산',
    'VPS_VPS': '재학생 1인당 도서관방문자수',
    'VUC_UC_LUC': '봉사대상자수 및 이용자수_도서관 이용자수'
};

// 차트 타입별 한글명
const CHART_TYPE_NAMES = {
    'bar': '막대 차트',
    'line': '선 차트',
    'scatter': '산점도',
    'pie': '원형 차트'
};

// 정렬 방식별 한글명
const SORT_ORDER_NAMES = {
    'year_score': '연도별 → 점수 오름차순',
    'score_only': '전체 점수 오름차순', 
    'score_desc': '전체 점수 내림차순',
    'university': '대학명 가나다순'
};

// CSV 파일 로드
async function loadCSVData() {
    try {
        console.log('CSV 파일 로딩 중...');
        
        // CSV 파일 경로
        const csvPath = '../../resource/csv_files/필터링데이터.csv';
        
        const response = await fetch(csvPath);
        if (!response.ok) {
            throw new Error(`CSV 파일 로드 실패: ${response.status}`);
        }
        
        const csvText = await response.text();
        
        // CSV 파싱
        csvData = parseCSV(csvText);
        
        console.log('CSV 데이터 로드 완료:', csvData.length, '행');
        console.log('컬럼명:', Object.keys(csvData[0] || {}));
        
        // 피처 선택 옵션 업데이트
        updateFeatureOptions();
        
        return csvData;
    } catch (error) {
        console.error('CSV 로드 실패:', error);
        showError(`CSV 파일을 불러올 수 없습니다: ${error.message}`);
        return null;
    }
}

// CSV 파싱 함수
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const data = [];
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length === headers.length) {
            const row = {};
            headers.forEach((header, index) => {
                const value = values[index];
                // 숫자 변환 시도
                const numValue = parseFloat(value);
                row[header] = isNaN(numValue) ? value : numValue;
            });
            data.push(row);
        }
    }
    
    return data;
}

// CSV 라인 파싱 (쉼표와 따옴표 처리)
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result.map(val => val.replace(/"/g, ''));
}

// 피처 선택 옵션 업데이트
function updateFeatureOptions() {
    if (!csvData || csvData.length === 0) return;
    
    const featureSelect = document.getElementById('featureSelect');
    const columns = Object.keys(csvData[0]);
    
    // 기존 옵션 제거
    featureSelect.innerHTML = '';
    
    // 새 옵션 추가
    columns.forEach(column => {
        if (column !== 'SNM' && column !== 'YR') { // 학교명, 연도는 제외
            const option = document.createElement('option');
            option.value = column;
            option.textContent = FEATURE_NAMES[column] || column;
            featureSelect.appendChild(option);
        }
    });
    
    // 기본값 설정
    if (columns.includes('LPS_LPS')) {
        featureSelect.value = 'LPS_LPS';
    }
}

// CSV 데이터로 차트 생성
async function generateChartFromCSV() {
    if (!csvData) {
        await loadCSVData();
        if (!csvData) return;
    }
    
    const featureSelect = document.getElementById('featureSelect');
    const chartTypeSelect = document.getElementById('chartType');
    const dataRangeSelect = document.getElementById('dataRange');
    
    const feature = featureSelect.value;
    const chartType = chartTypeSelect.value;
    const dataRange = dataRangeSelect.value;
    
    console.log('차트 생성 요청:', { feature, chartType, dataRange });
    
    if (!feature) {
        showError('분석할 변수를 선택해주세요.');
        return;
    }
    
    // 로딩 표시
    showLoading();
    
    try {
        // 데이터 처리
        const processedData = processCSVDataForChart(csvData, feature, dataRange);
        
        if (processedData && processedData.length > 0) {
            // 차트 생성
            createChart(processedData, chartType, feature);
            updateDataCount(processedData.length);
            
            // 플레이스홀더 숨기기
            document.getElementById('chartPlaceholder').style.display = 'none';
        } else {
            showError('선택한 조건에 해당하는 데이터가 없습니다.');
        }
    } catch (error) {
        console.error('차트 생성 실패:', error);
        showError('차트 생성 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// CSV 데이터 처리
function processCSVDataForChart(data, feature, dataRange) {
    // 유효한 데이터만 필터링
    let filteredData = data.filter(row => {
        return row[feature] !== null && 
               row[feature] !== undefined && 
               row[feature] !== '' &&
               !isNaN(parseFloat(row[feature])) &&
               row['SNM'] && 
               row['YR'];
    });
    
    // 정렬 방식 적용
    const sortOrder = document.getElementById('sortOrder').value;
    applySorting(filteredData, sortOrder);
    
    // 데이터 범위 적용
    switch(dataRange) {
        case 'top10':
            filteredData = filteredData.slice(-10);
            break;
        case 'top20':
            filteredData = filteredData.slice(-20);
            break;
        case 'bottom10':
            filteredData = filteredData.slice(0, 10);
            break;
        case 'bottom20':
            filteredData = filteredData.slice(0, 20);
            break;
        // 'all'은 그대로 사용
    }
    
    // 차트용 데이터 변환
    return filteredData.map(row => ({
        university: row['SNM'] || 'Unknown',
        year: row['YR'] || 'Unknown',
        value: parseFloat(row[feature]) || 0,
        score: parseFloat(row['SCR']) || 0,
        label: `${row['SNM']} (${row['YR']}) (${row['SCR']})`
    }));
}

// 정렬 적용 함수
function applySorting(data, sortOrder) {
    switch(sortOrder) {
        case 'year_score':
            // 기존 방식: 연도별로 묶고 점수 오름차순
            data.sort((a, b) => {
                const yearA = parseInt(a['YR']) || 0;
                const yearB = parseInt(b['YR']) || 0;
                const scrA = parseFloat(a['SCR']) || 0;
                const scrB = parseFloat(b['SCR']) || 0;
                
                if (yearA !== yearB) {
                    return yearA - yearB;
                }
                return scrA - scrB;
            });
            break;
            
        case 'score_only':
            // 모든 연도에서 점수 오름차순
            data.sort((a, b) => {
                const scrA = parseFloat(a['SCR']) || 0;
                const scrB = parseFloat(b['SCR']) || 0;
                return scrA - scrB;
            });
            break;
            
        case 'score_desc':
            // 모든 연도에서 점수 내림차순
            data.sort((a, b) => {
                const scrA = parseFloat(a['SCR']) || 0;
                const scrB = parseFloat(b['SCR']) || 0;
                return scrB - scrA;
            });
            break;
            
        case 'university':
            // 대학명 가나다순
            data.sort((a, b) => {
                const nameA = (a['SNM'] || '').toString();
                const nameB = (b['SNM'] || '').toString();
                return nameA.localeCompare(nameB, 'ko');
            });
            break;
    }
}

// Chart.js를 사용한 차트 생성
function createChart(data, chartType, feature) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // 기존 차트 제거
    if (currentChart) {
        currentChart.destroy();
    }
    
    chartData = data;
    
    const labels = data.map(item => item.label);
    const values = data.map(item => item.value);
    
    const chartConfig = {
        type: chartType === 'scatter' ? 'scatter' : chartType,
        data: {
            labels: labels,
            datasets: [{
                label: FEATURE_NAMES[feature] || feature,
                data: chartType === 'scatter' ? 
                    data.map((item, index) => ({x: index, y: item.value})) : 
                    values,
                backgroundColor: chartType === 'pie' ? 
                    CHART_COLORS.slice(0, data.length) : 
                    CHART_COLORS[0] + '80',
                borderColor: CHART_COLORS[0],
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `[${FEATURE_NAMES[feature] || feature}] vs 대학 이름 (SCR 기준 오름차순)`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#42a5f5'
                },
                legend: {
                    display: chartType === 'pie',
                    position: 'bottom'
                }
            },
            scales: getScaleConfig(chartType, feature),
            elements: {
                point: {
                    radius: chartType === 'scatter' ? 6 : 3,
                    hoverRadius: 8
                }
            }
        }
    };
    
    currentChart = new Chart(ctx, chartConfig);
}

// 차트 타입별 스케일 설정
function getScaleConfig(chartType, feature) {
    if (chartType === 'pie') {
        return {};
    }
    
    return {
        x: {
            display: true,
            title: {
                display: true,
                text: '대학교 (개별 행)',
                color: '#666'
            },
            ticks: {
                maxRotation: 90,
                minRotation: 90,
                font: {
                    size: 10
                }
            }
        },
        y: {
            display: true,
            title: {
                display: true,
                text: FEATURE_NAMES[feature] || feature,
                color: '#666'
            },
            beginAtZero: false
        }
    };
}

// 평균값 데이터로 차트 업데이트
function updateChartWithAverageData() {
    if (!chartData) return;
    
    // 대학별 평균 계산
    const universityAvg = {};
    chartData.forEach(item => {
        if (!universityAvg[item.university]) {
            universityAvg[item.university] = [];
        }
        universityAvg[item.university].push(item.value);
    });
    
    const avgData = Object.keys(universityAvg).map(uni => ({
        university: uni,
        value: universityAvg[uni].reduce((a, b) => a + b, 0) / universityAvg[uni].length,
        label: `${uni} (평균)`,
        year: '평균',
        score: 0
    }));
    
    // 평균값 기준으로 정렬
    avgData.sort((a, b) => a.value - b.value);
    
    const feature = document.getElementById('featureSelect').value;
    const chartType = document.getElementById('chartType').value;
    createChart(avgData, chartType, feature);
}

// 나머지 함수들 (기존과 동일)
function navigateTo(page) {
    console.log(`${page} 페이지로 이동`);
    
    switch(page) {
        case 'learning':
            location.reload();
            break;
        case 'development':
            window.location.href = 'page_prediction_num01.html';
            break;
        case 'myservice':
            alert('마이 서비스 페이지로 이동합니다.');
            break;
        case 'mypage':
            alert('마이 페이지로 이동합니다.');
            break;
        case 'main':
            window.location.href = 'page_mainpage_num01.html'; // 메인페이지로 이동
            break;
        default:
            alert('페이지를 찾을 수 없습니다.');
    }
}

function onTableChange() {
    console.log('테이블 변경 - CSV 모드에서는 필터링데이터.csv 사용');
    updateCurrentInfo();
}

function onFeatureChange() {
    updateCurrentInfo();
}

function onChartTypeChange() {
    updateCurrentInfo();
    if (currentChart && chartData) {
        const chartType = document.getElementById('chartType').value;
        const feature = document.getElementById('featureSelect').value;
        createChart(chartData, chartType, feature);
    }
}

function onDataRangeChange() {
    if (currentChart) {
        generateChartFromCSV();
    }
}

// 정렬 방식 변경 처리
function onSortOrderChange() {
    console.log('정렬 방식 변경');
    updateCurrentInfo();
    
    // 차트가 있다면 새로운 정렬로 다시 생성
    if (currentChart) {
        generateChartFromCSV();
    }
}

function switchTab(tabName) {
    const tabs = document.querySelectorAll('.chart-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    event.target.classList.add('active');
    
    console.log('탭 전환:', tabName);
    
    if (tabName === 'table2') {
        // 평균값 테이블로 전환
        updateChartWithAverageData();
    } else {
        // 원본 데이터로 복원 - 전체 데이터를 다시 생성
        console.log('원본 데이터로 복원');
        generateChartFromCSV();
    }
}

function updateCurrentInfo() {
    const tableSelect = document.getElementById('tableSelect');
    const featureSelect = document.getElementById('featureSelect');
    const chartTypeSelect = document.getElementById('chartType');
    const sortOrderSelect = document.getElementById('sortOrder');
    
    document.getElementById('currentTable').textContent = '필터링데이터.csv';
    document.getElementById('currentFeature').textContent = FEATURE_NAMES[featureSelect.value] || featureSelect.value;
    document.getElementById('currentChartType').textContent = CHART_TYPE_NAMES[chartTypeSelect.value];
    document.getElementById('currentSortOrder').textContent = SORT_ORDER_NAMES[sortOrderSelect.value];
}

function updateDataCount(count) {
    document.getElementById('dataCount').textContent = `${count}개`;
}

function showLoading() {
    document.getElementById('chartLoading').style.display = 'flex';
    document.getElementById('chartPlaceholder').style.display = 'none';
}

function hideLoading() {
    document.getElementById('chartLoading').style.display = 'none';
}

function showError(message) {
    const placeholder = document.getElementById('chartPlaceholder');
    placeholder.innerHTML = `
        <div class="placeholder-content">
            <div class="placeholder-icon">⚠️</div>
            <h3>오류 발생</h3>
            <p>${message}</p>
        </div>
    `;
    placeholder.style.display = 'flex';
    hideLoading();
}

function exportChart() {
    if (!currentChart) {
        alert('내보낼 차트가 없습니다. 먼저 차트를 생성해주세요.');
        return;
    }
    
    try {
        const canvas = document.getElementById('mainChart');
        const url = canvas.toDataURL('image/png');
        
        const a = document.createElement('a');
        a.href = url;
        const feature = document.getElementById('featureSelect').value;
        a.download = `libra_chart_${FEATURE_NAMES[feature] || feature}_${new Date().getTime()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        console.log('차트 내보내기 완료');
    } catch (error) {
        console.error('차트 내보내기 실패:', error);
        alert('차트 내보내기에 실패했습니다.');
    }
}

function saveAnalysis() {
    const currentConfig = {
        table: '필터링데이터.csv',
        feature: document.getElementById('featureSelect').value,
        chartType: document.getElementById('chartType').value,
        dataRange: document.getElementById('dataRange').value,
        timestamp: new Date().toISOString()
    };
    
    const savedAnalyses = JSON.parse(localStorage.getItem('libra_saved_analyses') || '[]');
    savedAnalyses.push(currentConfig);
    localStorage.setItem('libra_saved_analyses', JSON.stringify(savedAnalyses));
    
    alert('현재 분석 설정이 즐겨찾기에 저장되었습니다.');
    console.log('분석 저장 완료:', currentConfig);
}

// generateChart 함수를 CSV 버전으로 대체
function generateChart() {
    generateChartFromCSV();
}

// 페이지 초기화
function initializePage() {
    console.log('CSV 기반 학습환경 분석 페이지 초기화');
    updateCurrentInfo();
    
    // CSV 데이터 로드
    loadCSVData();
    
    // 이벤트 리스너 등록
    setupEventListeners();
}

function setupEventListeners() {
    const panelSections = document.querySelectorAll('.panel-section');
    panelSections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.1}s`;
        section.style.animation = 'fadeInUp 0.6s ease-out both';
    });
}

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        generateChartFromCSV();
    }
    
    if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        exportChart();
    }
    
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        saveAnalysis();
    }
});

// 페이지 로드 완료 시 초기화
window.addEventListener('load', initializePage);

document.addEventListener('DOMContentLoaded', function() {
    console.log('CSV 기반 학습환경 분석 페이지 DOM 로드 완료');
});

window.addEventListener('beforeunload', function() {
    if (currentChart) {
        currentChart.destroy();
    }
    console.log('학습환경 분석 페이지를 떠납니다.');
});