// 학습환경 예측 페이지 스크립트
// 파일명: script_prediction_page.js

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

// 차트 타입별 한글명
const CHART_TYPE_NAMES = {
    'bar': '막대 차트',
    'line': '선 차트',
    'scatter': '산점도',
    'pie': '원형 차트'
};

// 정렬 방식별 한글명
const SORT_ORDER_NAMES = {
    'default': '기본 순서',
    'asc': '오름차순',
    'desc': '내림차순',
    'alphabetical': '가나다순'
};

// CSV 파일 로드 (동적 파일 선택 지원)
async function loadCSVData(fileName = null) {
    try {
        // 파일명이 지정되지 않으면 현재 선택된 파일 사용
        if (!fileName) {
            const tableSelect = document.getElementById('tableSelect');
            fileName = tableSelect.value;
        }
        
        console.log('예측 CSV 파일 로딩 중:', fileName);
        
        // CSV 파일 경로
        const csvPath = `../../resource/csv_files/csv_data/${fileName}`;
        
        const response = await fetch(csvPath);
        if (!response.ok) {
            throw new Error(`CSV 파일 로드 실패: ${response.status}`);
        }
        
        const csvText = await response.text();
        
        // CSV 파싱
        csvData = parseCSV(csvText);
        
        console.log(`${fileName} 데이터 로드 완료:`, csvData.length, '행');
        console.log('컬럼명:', Object.keys(csvData[0] || {}));
        
        // 피처 선택 옵션 업데이트
        updateFeatureOptions();
        
        // 현재 정보 업데이트
        updateCurrentInfo();
        
        return csvData;
    } catch (error) {
        console.error('예측 CSV 로드 실패:', error);
        showError(`예측 데이터 파일을 불러올 수 없습니다: ${error.message}`);
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
    
    // 새 옵션 추가 - 모든 컬럼을 옵션으로 추가
    columns.forEach(column => {
        const option = document.createElement('option');
        option.value = column;
        option.textContent = column;
        featureSelect.appendChild(option);
    });
    
    // SCR_EST를 기본값으로 설정 (있는 경우)
    if (columns.includes('SCR_EST')) {
        featureSelect.value = 'SCR_EST';
    } else {
        // SCR_EST가 없으면 첫 번째 숫자 컬럼을 기본값으로 설정
        const firstNumericColumn = columns.find(col => 
            csvData.some(row => !isNaN(parseFloat(row[col])))
        );
        if (firstNumericColumn) {
            featureSelect.value = firstNumericColumn;
        }
    }
}

// 예측 CSV 데이터로 차트 생성
async function generateChartFromCSV() {
    // 현재 선택된 파일로 데이터 로드
    const tableSelect = document.getElementById('tableSelect');
    const selectedFile = tableSelect.value;
    
    if (!csvData) {
        await loadCSVData(selectedFile);
        if (!csvData) return;
    }
    
    const featureSelect = document.getElementById('featureSelect');
    const chartTypeSelect = document.getElementById('chartType');
    const dataRangeSelect = document.getElementById('dataRange');
    
    const feature = featureSelect.value;
    const chartType = chartTypeSelect.value;
    const dataRange = dataRangeSelect.value;
    
    console.log('예측 차트 생성 요청:', { file: selectedFile, feature, chartType, dataRange });
    
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
        console.error('예측 차트 생성 실패:', error);
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
               !isNaN(parseFloat(row[feature]));
    });
    
    // 정렬 방식 적용
    const sortOrder = document.getElementById('sortOrder').value;
    applySorting(filteredData, feature, sortOrder);
    
    // 데이터 범위 적용
    switch(dataRange) {
        case 'top10':
            filteredData = filteredData.slice(-10);
            break;
        case 'top20':
            filteredData = filteredData.slice(-20);
            break;
        case 'top50':
            filteredData = filteredData.slice(-50);
            break;
        case 'bottom10':
            filteredData = filteredData.slice(0, 10);
            break;
        case 'bottom20':
            filteredData = filteredData.slice(0, 20);
            break;
        case 'bottom50':
            filteredData = filteredData.slice(0, 50);
            break;
        // 'all'은 그대로 사용
    }
    
    // 차트용 데이터 변환
    return filteredData.map((row, index) => ({
        label: generateLabel(row, index),
        value: parseFloat(row[feature]) || 0,
        originalData: row
    }));
}

// 라벨 생성 (첫 번째 문자열 컬럼 또는 인덱스 사용)
function generateLabel(row, index) {
    // 첫 번째 문자열 컬럼 찾기
    const stringColumns = Object.keys(row).filter(key => 
        typeof row[key] === 'string' && row[key].trim() !== ''
    );
    
    if (stringColumns.length > 0) {
        return `${row[stringColumns[0]]} (${index + 1})`;
    }
    
    return `데이터 ${index + 1}`;
}

// 정렬 적용 함수
function applySorting(data, feature, sortOrder) {
    switch(sortOrder) {
        case 'asc':
            data.sort((a, b) => {
                const valA = parseFloat(a[feature]) || 0;
                const valB = parseFloat(b[feature]) || 0;
                return valA - valB;
            });
            break;
            
        case 'desc':
            data.sort((a, b) => {
                const valA = parseFloat(a[feature]) || 0;
                const valB = parseFloat(b[feature]) || 0;
                return valB - valA;
            });
            break;
            
        case 'alphabetical':
            // 첫 번째 문자열 컬럼 기준 정렬
            const stringColumn = Object.keys(data[0] || {}).find(key => 
                typeof data[0][key] === 'string'
            );
            if (stringColumn) {
                data.sort((a, b) => {
                    const nameA = (a[stringColumn] || '').toString();
                    const nameB = (b[stringColumn] || '').toString();
                    return nameA.localeCompare(nameB, 'ko');
                });
            }
            break;
            
        case 'default':
        default:
            // 기본 순서 유지
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
                label: feature,
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
                    text: `[${feature}] 예측 분석`,
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
                text: '데이터 항목',
                color: '#666'
            },
            ticks: {
                maxRotation: 45,
                minRotation: 45,
                font: {
                    size: 10
                }
            }
        },
        y: {
            display: true,
            title: {
                display: true,
                text: feature,
                color: '#666'
            },
            beginAtZero: false
        }
    };
}

// 통계 분석 데이터로 차트 업데이트
function updateChartWithStats() {
    if (!chartData) return;
    
    const feature = document.getElementById('featureSelect').value;
    const values = chartData.map(item => item.value);
    
    // 기본 통계 계산
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const median = values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
    
    const statsData = [
        { label: '평균값', value: avg },
        { label: '최대값', value: max },
        { label: '최소값', value: min },
        { label: '중간값', value: median }
    ];
    
    const chartType = document.getElementById('chartType').value;
    createChart(statsData, chartType, `${feature} 통계`);
}

// 이벤트 핸들러들
function navigateTo(page) {
    console.log(`${page} 페이지로 이동`);
    
    switch(page) {
        case 'learning':
            window.location.href = 'page_chartpage_num01.html';
            break;
        case 'prediction':
            location.reload();
            break;
        case 'myservice':
            alert('마이 서비스 페이지로 이동합니다.');
            break;
        case 'mypage':
            alert('마이 페이지로 이동합니다.');
            break;
        case 'main':
            window.location.href = 'page_mainpage_num01.html';
            break;
        default:
            alert('페이지를 찾을 수 없습니다.');
    }
}

function onTableChange() {
    const tableSelect = document.getElementById('tableSelect');
    const selectedFile = tableSelect.value;
    
    console.log('예측 테이블 변경:', selectedFile);
    
    // 로딩 표시
    showLoading();
    
    // 새로운 CSV 파일 로드
    loadCSVData(selectedFile).then(() => {
        // 기존 차트가 있다면 제거
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }
        
        // 플레이스홀더 다시 표시
        document.getElementById('chartPlaceholder').style.display = 'flex';
        hideLoading();
        
        // 현재 정보 업데이트
        updateCurrentInfo();
        
        console.log('새로운 데이터셋 로드 완료');
    }).catch(error => {
        console.error('데이터셋 변경 실패:', error);
        hideLoading();
    });
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

function onSortOrderChange() {
    console.log('정렬 방식 변경');
    updateCurrentInfo();
    
    if (currentChart) {
        generateChartFromCSV();
    }
}

function onDataRangeChange() {
    if (currentChart) {
        generateChartFromCSV();
    }
}

function switchTab(tabName) {
    const tabs = document.querySelectorAll('.chart-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    event.target.classList.add('active');
    
    console.log('탭 전환:', tabName);
    
    if (tabName === 'prediction2') {
        updateChartWithStats();
    } else {
        generateChartFromCSV();
    }
}

function updateCurrentInfo() {
    const featureSelect = document.getElementById('featureSelect');
    const chartTypeSelect = document.getElementById('chartType');
    const sortOrderSelect = document.getElementById('sortOrder');
    
    document.getElementById('currentTable').textContent = '환경점수예측_2014';
    document.getElementById('currentFeature').textContent = featureSelect.value || '-';
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
        a.download = `libra_prediction_chart_${feature}_${new Date().getTime()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        console.log('예측 차트 내보내기 완료');
    } catch (error) {
        console.error('차트 내보내기 실패:', error);
        alert('차트 내보내기에 실패했습니다.');
    }
}

function saveAnalysis() {
    const tableSelect = document.getElementById('tableSelect');
    const fileName = tableSelect.value;
    const year = fileName.match(/(\d{4})/)?.[1] || '2014';
    
    const currentConfig = {
        table: `환경점수예측_${year}.csv`,
        fileName: fileName,
        feature: document.getElementById('featureSelect').value,
        chartType: document.getElementById('chartType').value,
        sortOrder: document.getElementById('sortOrder').value,
        dataRange: document.getElementById('dataRange').value,
        timestamp: new Date().toISOString()
    };
    
    const savedAnalyses = JSON.parse(localStorage.getItem('libra_saved_predictions') || '[]');
    savedAnalyses.push(currentConfig);
    localStorage.setItem('libra_saved_predictions', JSON.stringify(savedAnalyses));
    
    alert(`${year}년 예측 분석 설정이 즐겨찾기에 저장되었습니다.`);
    console.log('예측 분석 저장 완료:', currentConfig);
}

// generateChart 함수를 CSV 버전으로 대체
function generateChart() {
    generateChartFromCSV();
}

// 페이지 초기화
function initializePage() {
    console.log('학습환경 예측 페이지 초기화');
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
    console.log('학습환경 예측 페이지 DOM 로드 완료');
});

window.addEventListener('beforeunload', function() {
    if (currentChart) {
        currentChart.destroy();
    }
    console.log('학습환경 예측 페이지를 떠납니다.');
});