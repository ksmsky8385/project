// 가능성 예측 페이지 스크립트 (예측데이터총합.csv 사용)
// 파일명: script_prediction_page.js

// 전역 변수
let csvData = null;
let filteredData = null;
let selectedUniversities = new Set();
let trendChart = null;
let pieChart = null;
let availableYears = [];
let selectionMode = 'all'; // 'all' 또는 'manual'
let selectedYearRange = { start: 0, end: 0 };
let selectedDataRange = { start: 1, end: 1 };
let showAverage = true; // 평균값 그래프 표시 여부

// 차트 색상 팔레트
const CHART_COLORS = {
    primary: '#42a5f5',
    secondary: '#29b6f6',
    positive: '#4caf50',
    negative: '#f44336',
    neutral: '#9e9e9e'
};

// CSV 파일 로드 (예측데이터총합.csv 사용)
async function loadCSVData() {
    try {
        console.log('예측데이터총합.csv 파일 로딩 중...');
        
        // 통합 CSV 파일 경로로 변경
        const csvPath = '../../resource/csv_files/예측데이터총합.csv';
        
        const response = await fetch(csvPath);
        if (!response.ok) {
            throw new Error(`CSV 파일 로드 실패: ${response.status}`);
        }
        
        const csvText = await response.text();
        
        // CSV 파싱
        csvData = parseCSV(csvText);
        
        console.log('CSV 데이터 로드 완료:', csvData.length, '행');
        console.log('컬럼명:', Object.keys(csvData[0] || {}));
        
        // 연도 정보 추출 (동적으로 모든 SCR_EST_YYYY 컬럼 감지)
        extractYears();
        
        // 필터 옵션 업데이트
        updateFilterOptions();
        
        // 연도 슬라이더 초기화
        initializeYearSliders();
        
        // 데이터 범위 슬라이더 초기화
        selectedDataRange = { start: 1, end: Math.min(50, csvData.length) }; // 기본값: 처음 50개
        updateDataRangeSliders();
        
        // 초기 필터 적용하여 대학 목록 준비
        console.log('초기 필터 적용 중...');
        applyFilters();
        
        return csvData;
    } catch (error) {
        console.error('CSV 로드 실패:', error);
        showError(`데이터 파일을 불러올 수 없습니다: ${error.message}`);
        return null;
    }
}

// CSV 파싱 함수
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) {
        throw new Error('CSV 파일이 비어있거나 형식이 올바르지 않습니다.');
    }
    
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    console.log('발견된 헤더:', headers);
    
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

// 연도 정보 추출 (동적 감지)
function extractYears() {
    if (!csvData || csvData.length === 0) return;
    
    const firstRow = csvData[0];
    availableYears = [];
    
    // SCR_EST_YYYY 형태의 컬럼명에서 연도 추출 (범위 제한 없이)
    Object.keys(firstRow).forEach(key => {
        const match = key.match(/^SCR_EST_(\d{4})$/);
        if (match) {
            const year = parseInt(match[1]);
            // 연도가 4자리 숫자이고 합리적인 범위 내에 있으면 추가
            if (year >= 1900 && year <= 2100) {
                availableYears.push(year);
            }
        }
    });
    
    // 연도 정렬 (오름차순)
    availableYears.sort((a, b) => a - b);
    
    console.log('CSV에서 감지된 사용 가능한 연도:', availableYears);
    console.log('연도 범위:', availableYears.length > 0 ? `${Math.min(...availableYears)} ~ ${Math.max(...availableYears)}` : '없음');
}

// 필터 옵션 업데이트
function updateFilterOptions() {
    if (!csvData || csvData.length === 0) return;
    
    // 각 필터별 고유값 추출
    const stypValues = new Set();
    const fndValues = new Set();
    const rgnValues = new Set();
    const uscValues = new Set();
    
    csvData.forEach(row => {
        if (row.STYP) stypValues.add(row.STYP);
        if (row.FND) fndValues.add(row.FND);
        if (row.RGN) rgnValues.add(row.RGN);
        if (row.USC) uscValues.add(row.USC);
    });
    
    // 필터 옵션 업데이트
    updateSelectOptions('stypFilter', Array.from(stypValues).sort());
    updateSelectOptions('fndFilter', Array.from(fndValues).sort());
    updateSelectOptions('rgnFilter', Array.from(rgnValues).sort());
    updateSelectOptions('uscFilter', Array.from(uscValues).sort());
}

// Select 옵션 업데이트
function updateSelectOptions(selectId, values) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // 기존 옵션 제거 (전체 옵션 제외)
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // 새 옵션 추가
    values.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    });
}

// 연도 범위 슬라이더 초기화
function initializeYearSliders() {
    if (availableYears.length === 0) return;
    
    const startSlider = document.getElementById('yearStartSlider');
    const endSlider = document.getElementById('yearEndSlider');
    const minLabel = document.getElementById('minYearLabel');
    const maxLabel = document.getElementById('maxYearLabel');
    
    // 슬라이더 범위 설정
    startSlider.min = 0;
    startSlider.max = availableYears.length - 1;
    startSlider.value = 0;
    
    endSlider.min = 0;
    endSlider.max = availableYears.length - 1;
    endSlider.value = availableYears.length - 1;
    
    // 레이블 업데이트
    minLabel.textContent = availableYears[0];
    maxLabel.textContent = availableYears[availableYears.length - 1];
    
    // 초기 범위 설정
    selectedYearRange.start = 0;
    selectedYearRange.end = availableYears.length - 1;
    
    updateSelectedYearRangeDisplay();
}

// 연도 슬라이더 변경 이벤트
function onYearSliderChange() {
    const startSlider = document.getElementById('yearStartSlider');
    const endSlider = document.getElementById('yearEndSlider');
    
    let startIdx = parseInt(startSlider.value);
    let endIdx = parseInt(endSlider.value);
    
    // 시작이 끝보다 크면 조정
    if (startIdx > endIdx) {
        if (event.target.id === 'yearStartSlider') {
            endIdx = startIdx;
            endSlider.value = endIdx;
        } else {
            startIdx = endIdx;
            startSlider.value = startIdx;
        }
    }
    
    selectedYearRange.start = startIdx;
    selectedYearRange.end = endIdx;
    
    updateSelectedYearRangeDisplay();
    
    // 차트가 있으면 업데이트
    if (trendChart || pieChart) {
        generateChart();
    }
}

// 선택된 연도 범위 표시 업데이트
function updateSelectedYearRangeDisplay() {
    const rangeDisplay = document.getElementById('selectedYearRange');
    const startYear = availableYears[selectedYearRange.start];
    const endYear = availableYears[selectedYearRange.end];
    
    rangeDisplay.textContent = `${startYear}년 ~ ${endYear}년`;
    updateCurrentInfo();
}

// 데이터 범위 슬라이더 초기화/업데이트
function updateDataRangeSliders() {
    const filtered = applyFilters();
    const dataCount = filtered.length;
    
    const startSlider = document.getElementById('dataStartSlider');
    const endSlider = document.getElementById('dataEndSlider');
    const minLabel = document.getElementById('dataMinLabel');
    const maxLabel = document.getElementById('dataMaxLabel');
    const countInfo = document.getElementById('dataCountInfo');
    
    // 필터링된 데이터 개수 표시
    countInfo.textContent = `필터링된 데이터: ${dataCount}개`;
    
    if (dataCount === 0) {
        // 데이터가 없을 때
        startSlider.min = 1;
        startSlider.max = 1;
        startSlider.value = 1;
        endSlider.min = 1;
        endSlider.max = 1;
        endSlider.value = 1;
        minLabel.textContent = '1';
        maxLabel.textContent = '1';
        document.getElementById('selectedDataRange').textContent = '데이터 없음';
        return;
    }
    
    // 슬라이더 범위 설정
    startSlider.min = 1;
    startSlider.max = dataCount;
    endSlider.min = 1;
    endSlider.max = dataCount;
    
    // 현재 값이 범위를 벗어나면 조정
    if (selectedDataRange.start > dataCount) {
        selectedDataRange.start = 1;
    }
    if (selectedDataRange.end > dataCount) {
        selectedDataRange.end = dataCount;
    }
    
    startSlider.value = selectedDataRange.start;
    endSlider.value = selectedDataRange.end;
    
    // 레이블 업데이트
    minLabel.textContent = '1';
    maxLabel.textContent = dataCount.toString();
    
    updateSelectedDataRangeDisplay();
}

// 데이터 슬라이더 변경 이벤트
function onDataSliderChange() {
    const startSlider = document.getElementById('dataStartSlider');
    const endSlider = document.getElementById('dataEndSlider');
    
    let startIdx = parseInt(startSlider.value);
    let endIdx = parseInt(endSlider.value);
    
    // 시작이 끝보다 크면 조정
    if (startIdx > endIdx) {
        if (event.target.id === 'dataStartSlider') {
            endIdx = startIdx;
            endSlider.value = endIdx;
        } else {
            startIdx = endIdx;
            startSlider.value = startIdx;
        }
    }
    
    selectedDataRange.start = startIdx;
    selectedDataRange.end = endIdx;
    
    updateSelectedDataRangeDisplay();
}

// 선택된 데이터 범위 표시 업데이트
function updateSelectedDataRangeDisplay() {
    const rangeDisplay = document.getElementById('selectedDataRange');
    const totalCount = parseInt(document.getElementById('dataMaxLabel').textContent) || 0;
    
    if (totalCount === 0) {
        rangeDisplay.textContent = '데이터 없음';
        return;
    }
    
    const selectedCount = selectedDataRange.end - selectedDataRange.start + 1;
    rangeDisplay.textContent = `${selectedDataRange.start}번째 ~ ${selectedDataRange.end}번째 (${selectedCount}개)`;
}

// 필터링 적용 (이름순 정렬 추가)
function applyFilters() {
    if (!csvData) return [];
    
    const stypFilter = document.getElementById('stypFilter').value;
    const fndFilter = document.getElementById('fndFilter').value;
    const rgnFilter = document.getElementById('rgnFilter').value;
    const uscFilter = document.getElementById('uscFilter').value;
    
    filteredData = csvData.filter(row => {
        if (stypFilter !== '전체' && row.STYP !== stypFilter) return false;
        if (fndFilter !== '전체' && row.FND !== fndFilter) return false;
        if (rgnFilter !== '전체' && row.RGN !== rgnFilter) return false;
        if (uscFilter !== '전체' && row.USC !== uscFilter) return false;
        
        // 최소한 하나의 연도 데이터가 있는지 확인
        return availableYears.some(year => {
            const value = row[`SCR_EST_${year}`];
            return value !== null && value !== undefined && value !== '' && !isNaN(value);
        });
    });
    
    // 이름순으로 정렬
    filteredData.sort((a, b) => {
        const nameA = (a.SNM || '').toString();
        const nameB = (b.SNM || '').toString();
        return nameA.localeCompare(nameB, 'ko');
    });
    
    return filteredData;
}

// 대학 목록 업데이트
function updateUniversityList() {
    const listContainer = document.getElementById('universityList');
    if (!listContainer) {
        console.error('universityList 요소를 찾을 수 없습니다.');
        return;
    }
    
    const filtered = applyFilters();
    console.log(`필터링된 대학 수: ${filtered.length}개`);
    
    // 기존 목록 초기화
    listContainer.innerHTML = '';
    
    if (filtered.length === 0) {
        listContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">필터 조건에 맞는 대학이 없습니다.</div>';
        return;
    }
    
    filtered.forEach((row, index) => {
        const item = document.createElement('div');
        item.className = 'university-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `univ_${index}_${row.SNM}`;
        checkbox.value = row.SNM;
        checkbox.checked = selectedUniversities.has(row.SNM);
        checkbox.onchange = () => updateSelectedUniversities();
        
        const label = document.createElement('label');
        label.htmlFor = `univ_${index}_${row.SNM}`;
        label.textContent = row.SNM || 'Unknown';
        
        item.appendChild(checkbox);
        item.appendChild(label);
        listContainer.appendChild(item);
    });
    
    updateSelectedCount();
    console.log('대학 목록 DOM 업데이트 완료');
}

// 선택된 대학 업데이트
function updateSelectedUniversities() {
    selectedUniversities.clear();
    
    const checkboxes = document.querySelectorAll('#universityList input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        selectedUniversities.add(checkbox.value);
    });
    
    updateSelectedCount();
}

// 선택된 개수 업데이트
function updateSelectedCount() {
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = `${selectedUniversities.size}개 선택됨`;
    }
}

// 전체 선택/해제
function toggleAllUniversities() {
    const checkboxes = document.querySelectorAll('#universityList input[type="checkbox"]');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
    });
    
    updateSelectedUniversities();
}

// 평균값 그래프 표시 토글
function onShowAverageChange() {
    const checkbox = document.getElementById('showAverageCheckbox');
    showAverage = checkbox.checked;
    
    console.log('평균값 그래프 표시:', showAverage ? '켜짐' : '꺼짐');
    
    // 차트가 있으면 다시 생성
    if (trendChart && csvData) {
        const dataForChart = prepareChartData();
        if (dataForChart.length > 0) {
            createTrendChart(dataForChart);
        }
    }
}

// 선택 모드 설정
function setSelectionMode(mode) {
    selectionMode = mode;
    
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => btn.classList.remove('active'));
    
    // 클릭된 버튼을 활성화 (event.target 대신 직접 찾기)
    const clickedBtn = Array.from(modeBtns).find(btn => 
        (mode === 'all' && btn.textContent.includes('필터링 후 전체')) ||
        (mode === 'manual' && btn.textContent.includes('수동 선택'))
    );
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }
    
    const selector = document.getElementById('universitySelector');
    const dataRangeGroup = document.getElementById('dataRangeSliderGroup');
    
    console.log(`선택 모드 변경: ${mode}`);
    
    if (mode === 'manual') {
        // 수동 선택 모드
        selector.classList.add('active');
        dataRangeGroup.style.display = 'none';
        console.log('대학 목록 업데이트 시작...');
        updateUniversityList();
        console.log('대학 목록 업데이트 완료');
    } else {
        // 전체 모드
        selector.classList.remove('active');
        dataRangeGroup.style.display = 'block';
        selectedUniversities.clear();
        updateDataRangeSliders();
    }
    
    updateCurrentInfo();
}

// 차트 생성
async function generateChart() {
    if (!csvData) {
        await loadCSVData();
        if (!csvData) return;
    }
    
    showLoading();
    
    try {
        // 데이터 준비
        const dataForChart = prepareChartData();
        
        if (dataForChart.length === 0) {
            showError('선택한 조건에 해당하는 데이터가 없습니다.');
            return;
        }
        
        // 차트 생성
        createTrendChart(dataForChart);
        createTrendPieChart(dataForChart);
        
        // 정보 업데이트
        updateDataCount(dataForChart.length);
        
        // 플레이스홀더 숨기기
        document.getElementById('chartPlaceholder').style.display = 'none';
        document.querySelector('.chart-grid').style.display = 'grid';
        
    } catch (error) {
        console.error('차트 생성 실패:', error);
        showError('차트 생성 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// 차트 데이터 준비 (연도별 컬럼 사용)
function prepareChartData() {
    const filtered = applyFilters();
    let dataToUse = filtered;
    
    // 수동 선택 모드이고 선택된 대학이 있으면 필터링
    if (selectionMode === 'manual' && selectedUniversities.size > 0) {
        dataToUse = filtered.filter(row => selectedUniversities.has(row.SNM));
    } else {
        // 전체 모드일 때는 데이터 범위 슬라이더 적용
        const startIdx = selectedDataRange.start - 1; // 1부터 시작하므로 -1
        const endIdx = selectedDataRange.end;
        dataToUse = filtered.slice(startIdx, endIdx);
    }
    
    // 연도 범위 적용
    const startYear = availableYears[selectedYearRange.start];
    const endYear = availableYears[selectedYearRange.end];
    let yearsToUse = availableYears.filter(year => year >= startYear && year <= endYear);
    
    console.log(`차트 데이터 준비: ${dataToUse.length}개 대학, ${yearsToUse.length}개 연도 (${startYear}-${endYear})`);
    
    return dataToUse.map(row => ({
        university: row.SNM,
        styp: row.STYP,
        fnd: row.FND,
        rgn: row.RGN,
        usc: row.USC,
        years: yearsToUse,
        scores: yearsToUse.map(year => {
            const value = row[`SCR_EST_${year}`];
            return (value !== null && value !== undefined && value !== '' && !isNaN(value)) ? parseFloat(value) : null;
        })
    }));
}

// 추세 계산
function calculateTrend(scores) {
    // 마지막 2개년도 비교
    const validScores = scores.filter(s => s !== null);
    if (validScores.length < 2) return 'neutral';
    
    const lastScore = validScores[validScores.length - 1];
    const prevScore = validScores[validScores.length - 2];
    
    if (lastScore > prevScore) return 'upward';
    if (lastScore < prevScore) return 'downward';
    return 'neutral';
}

// 연도별 추이 차트 생성 (평균값 표시 옵션 포함)
function createTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    // 데이터셋 배열 초기화
    const datasets = [];
    
    // 평균값 그래프가 켜져있을 때만 추가
    if (showAverage) {
        // 평균 점수 계산
        const avgScores = data[0].years.map((year, idx) => {
            const scores = data.map(d => d.scores[idx]).filter(s => s !== null);
            return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
        });
        
        datasets.push({
            label: '전체 평균',
            data: avgScores,
            borderColor: CHART_COLORS.primary,
            backgroundColor: CHART_COLORS.primary + '20',
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: false,
            order: 1 // 평균선이 맨 앞에 오도록
        });
    }
    
    // 개별 대학 추가 (최대 20개까지만 개별 라인 표시)
    const maxIndividualLines = 20;
    const individualData = data.slice(0, Math.min(data.length, maxIndividualLines));
    individualData.forEach((univ, idx) => {
        const hue = idx * (360 / maxIndividualLines);
        const opacity = showAverage ? 0.7 : 1; // 평균선이 있을 때는 개별 라인을 약간 투명하게
        
        datasets.push({
            label: univ.university,
            data: univ.scores,
            borderColor: `hsla(${hue}, 70%, 50%, ${opacity})`,
            backgroundColor: `hsla(${hue}, 70%, 50%, 0.1)`,
            borderWidth: showAverage ? 1.5 : 2, // 평균선이 있을 때는 개별 라인을 약간 얇게
            tension: 0.4,
            pointRadius: 2,
            pointHoverRadius: 5,
            fill: false,
            order: 2 // 개별 라인들이 평균선 뒤에 오도록
        });
    });
    
    const config = {
        type: 'line',
        data: {
            labels: data[0].years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: data.length <= 20,
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: {
                            size: 11
                        },
                        filter: function(legendItem, chartData) {
                            // 평균값 그래프가 꺼져있을 때는 평균 라벨 숨김
                            if (!showAverage && legendItem.text === '전체 평균') {
                                return false;
                            }
                            return true;
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2) + '점';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: '연도'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: '환경점수'
                    },
                    beginAtZero: false
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    };
    
    trendChart = new Chart(ctx, config);
}

// 추세 비율 차트 생성
function createTrendPieChart(data) {
    const ctx = document.getElementById('trendPieChart').getContext('2d');
    
    if (pieChart) {
        pieChart.destroy();
    }
    
    // 각 대학의 추세 계산
    const trends = data.map(d => ({
        university: d.university,
        trend: calculateTrend(d.scores)
    }));
    
    const upwardCount = trends.filter(t => t.trend === 'upward').length;
    const downwardCount = trends.filter(t => t.trend === 'downward').length;
    const neutralCount = trends.filter(t => t.trend === 'neutral').length;
    
    // 백분율 계산
    const total = data.length;
    const upwardPercent = ((upwardCount / total) * 100).toFixed(1);
    const downwardPercent = ((downwardCount / total) * 100).toFixed(1);
    const neutralPercent = ((neutralCount / total) * 100).toFixed(1);
    
    // 통계 업데이트
    document.getElementById('upwardPercent').textContent = upwardPercent + '%';
    document.getElementById('downwardPercent').textContent = downwardPercent + '%';
    
    const config = {
        type: 'doughnut',
        data: {
            labels: ['상승 추세', '하락 추세', '변화 없음'],
            datasets: [{
                data: [upwardCount, downwardCount, neutralCount],
                backgroundColor: [
                    CHART_COLORS.positive,
                    CHART_COLORS.negative,
                    CHART_COLORS.neutral
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            
                            // 해당 카테고리의 대학 목록
                            const trendType = context.dataIndex === 0 ? 'upward' : 
                                            context.dataIndex === 1 ? 'downward' : 'neutral';
                            const universities = trends
                                .filter(t => t.trend === trendType)
                                .map(t => t.university)
                                .slice(0, 5); // 최대 5개만 표시
                            
                            return [
                                `${label}: ${value}개 (${percentage}%)`,
                                ...universities.map(u => `  • ${u}`),
                                universities.length < trends.filter(t => t.trend === trendType).length ? 
                                    `  ... 외 ${trends.filter(t => t.trend === trendType).length - 5}개` : ''
                            ].filter(Boolean);
                        }
                    }
                }
            }
        }
    };
    
    pieChart = new Chart(ctx, config);
}

// 이벤트 핸들러
function navigateTo(page) {
    switch(page) {
        case 'learning':
            window.location.href = 'page_chartpage_num01.html';
            break;
        case 'development':
            window.location.href = 'page_prediction_num01.html';
            break;
        case 'myservice':
            window.location.href = 'page_userpage_num01.html';  // 현재 페이지
            break;
        case 'mypage':
            alert('마이 페이지로 이동합니다.');
            break;
        case 'main':
            window.location.href = 'page_mainpage_num01.html';
            break;
    }
}

function onFilterChange() {
    console.log('필터 변경됨');
    updateCurrentInfo();
    
    // 데이터 범위 슬라이더 업데이트
    updateDataRangeSliders();
    
    // 수동 선택 모드일 때 대학 목록 업데이트
    if (selectionMode === 'manual') {
        console.log('수동 선택 모드에서 대학 목록 업데이트');
        updateUniversityList();
    }
    
    // 차트가 있으면 업데이트
    if (trendChart || pieChart) {
        generateChart();
    }
}

function updateCurrentInfo() {
    const startYear = availableYears[selectedYearRange.start] || '-';
    const endYear = availableYears[selectedYearRange.end] || '-';
    document.getElementById('currentYearRange').textContent = `${startYear}년 ~ ${endYear}년`;
    
    document.getElementById('currentStyp').textContent = document.getElementById('stypFilter').value;
    document.getElementById('currentFnd').textContent = document.getElementById('fndFilter').value;
    document.getElementById('currentRgn').textContent = document.getElementById('rgnFilter').value;
    document.getElementById('currentUsc').textContent = document.getElementById('uscFilter').value;
    document.getElementById('currentSelectionMode').textContent = 
        selectionMode === 'manual' ? '수동 선택' : '필터링 후 전체';
}

function updateDataCount(count) {
    document.getElementById('dataCount').textContent = `${count}개`;
}

function showLoading() {
    document.getElementById('chartLoading').style.display = 'flex';
    document.getElementById('chartPlaceholder').style.display = 'none';
    document.querySelector('.chart-grid').style.display = 'none';
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
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                파일 경로를 확인하세요: ../../resource/csv_files/예측데이터총합.csv
            </p>
        </div>
    `;
    placeholder.style.display = 'flex';
    document.querySelector('.chart-grid').style.display = 'none';
    hideLoading();
}

function exportCharts() {
    if (!trendChart || !pieChart) {
        alert('내보낼 차트가 없습니다. 먼저 차트를 생성해주세요.');
        return;
    }
    
    // 두 차트를 하나의 캔버스에 합치기
    const canvas1 = document.getElementById('trendChart');
    const canvas2 = document.getElementById('trendPieChart');
    
    const combinedCanvas = document.createElement('canvas');
    combinedCanvas.width = canvas1.width + canvas2.width + 20;
    combinedCanvas.height = Math.max(canvas1.height, canvas2.height);
    
    const ctx = combinedCanvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, combinedCanvas.width, combinedCanvas.height);
    
    ctx.drawImage(canvas1, 0, 0);
    ctx.drawImage(canvas2, canvas1.width + 20, 0);
    
    const url = combinedCanvas.toDataURL('image/png');
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `libra_prediction_analysis_${new Date().getTime()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    console.log('차트 내보내기 완료');
}

function saveAnalysis() {
    const currentConfig = {
        yearRange: {
            start: selectedYearRange.start,
            end: selectedYearRange.end,
            startYear: availableYears[selectedYearRange.start],
            endYear: availableYears[selectedYearRange.end]
        },
        dataRange: {
            start: selectedDataRange.start,
            end: selectedDataRange.end
        },
        showAverage: showAverage, // 평균값 표시 설정 저장
        styp: document.getElementById('stypFilter').value,
        fnd: document.getElementById('fndFilter').value,
        rgn: document.getElementById('rgnFilter').value,
        usc: document.getElementById('uscFilter').value,
        selectionMode: selectionMode,
        selectedUniversities: Array.from(selectedUniversities),
        timestamp: new Date().toISOString()
    };
    
    const savedAnalyses = JSON.parse(localStorage.getItem('libra_prediction_analyses') || '[]');
    savedAnalyses.push(currentConfig);
    localStorage.setItem('libra_prediction_analyses', JSON.stringify(savedAnalyses));
    
    alert('현재 분석 설정이 즐겨찾기에 저장되었습니다.');
    console.log('분석 저장 완료:', currentConfig);
}

// 페이지 초기화
function initializePage() {
    console.log('가능성 예측 페이지 초기화');
    updateCurrentInfo();
    
    // CSV 데이터 로드
    loadCSVData();
    
    // 이벤트 리스너 등록
    setupEventListeners();
}

function setupEventListeners() {
    // 애니메이션 효과
    const panelSections = document.querySelectorAll('.panel-section');
    panelSections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.1}s`;
        section.style.animation = 'fadeInUp 0.6s ease-out both';
    });
    
    // 차트 그리드 초기 숨김
    document.querySelector('.chart-grid').style.display = 'none';
}

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        generateChart();
    }
    
    if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        exportCharts();
    }
    
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        saveAnalysis();
    }
});

// 페이지 로드 완료 시 초기화
window.addEventListener('load', initializePage);

document.addEventListener('DOMContentLoaded', function() {
    console.log('가능성 예측 페이지 DOM 로드 완료');
});

window.addEventListener('beforeunload', function() {
    if (trendChart) {
        trendChart.destroy();
    }
    if (pieChart) {
        pieChart.destroy();
    }
    console.log('가능성 예측 페이지를 떠납니다.');
});

// 디버깅용 함수
function debugInfo() {
    console.log('=== 가능성 예측 디버깅 정보 ===');
    console.log('사용 가능한 연도:', availableYears);
    console.log('CSV 데이터:', csvData ? csvData.length + '행' : '없음');
    console.log('선택된 연도 범위:', {
        start: selectedYearRange.start,
        end: selectedYearRange.end,
        startYear: availableYears[selectedYearRange.start],
        endYear: availableYears[selectedYearRange.end]
    });
    console.log('평균값 표시:', showAverage);
    console.log('현재 차트:', {
        trendChart: trendChart ? '있음' : '없음',
        pieChart: pieChart ? '있음' : '없음'
    });
    
    if (csvData && csvData.length > 0) {
        console.log('컬럼명:', Object.keys(csvData[0]));
        
        // 점수 컬럼들 확인
        const scoreColumns = Object.keys(csvData[0]).filter(key => key.match(/^SCR_EST_\d{4}$/));
        console.log('점수 컬럼들:', scoreColumns);
        
        // 각 연도별 유효 데이터 수
        availableYears.forEach(year => {
            const validCount = csvData.filter(row => {
                const value = row[`SCR_EST_${year}`];
                return value !== null && value !== undefined && value !== '' && !isNaN(value);
            }).length;
            console.log(`${year}년: ${validCount}개 유효 데이터`);
        });
    }
}

// 개발자 도구용 전역 함수 등록
window.debugPrediction = debugInfo;
window.libraPrediction = {
    csvData,
    availableYears,
    selectedYearRange,
    selectedDataRange,
    selectionMode,
    selectedUniversities,
    generateChart,
    loadData: loadCSVData,
    debugInfo,
    // 수동 선택 모드 테스트
    testManualMode: function() {
        console.log('수동 선택 모드 테스트');
        console.log('현재 모드:', selectionMode);
        console.log('선택된 대학 수:', selectedUniversities.size);
        console.log('선택된 대학들:', Array.from(selectedUniversities));
        
        const selector = document.getElementById('universitySelector');
        const listContainer = document.getElementById('universityList');
        console.log('selector 표시 상태:', selector ? selector.classList.contains('active') : 'selector 없음');
        console.log('listContainer 내용:', listContainer ? listContainer.children.length + '개 항목' : 'listContainer 없음');
        
        if (listContainer && listContainer.children.length === 0) {
            console.log('대학 목록이 비어있음 - updateUniversityList() 실행');
            updateUniversityList();
        }
    },
    // 수동으로 모드 변경 테스트
    setManualMode: function() {
        setSelectionMode('manual');
    },
    setAllMode: function() {
        setSelectionMode('all');
    },
    // 연도별 데이터 테스트
    testYearData: function(year) {
        if (!csvData || !availableYears.includes(year)) {
            console.log(`${year}년 데이터가 없습니다.`);
            return;
        }
        
        const scoreColumn = `SCR_EST_${year}`;
        const validData = csvData.filter(row => {
            const value = row[scoreColumn];
            return value !== null && value !== undefined && value !== '' && !isNaN(value);
        });
        
        console.log(`${year}년 데이터 현황:`);
        console.log(`- 전체 데이터: ${csvData.length}개`);
        console.log(`- 유효 데이터: ${validData.length}개`);
        
        if (validData.length > 0) {
            const scores = validData.map(row => parseFloat(row[scoreColumn]));
            console.log(`- 점수 범위: ${Math.min(...scores)} ~ ${Math.max(...scores)}`);
            console.log(`- 평균 점수: ${(scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2)}`);
        }
    }
};