// 환경점수예측 분석 스크립트 (예측데이터총합.csv 사용)
// 파일명: script_chartpage_num01.js

// 전역 변수
let csvData = null;
let currentChart = null;
let chartData = null;
let currentYear = null;
let availableYears = [];

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
    'rank_asc': '환경점수 낮은 순',
    'rank_desc': '환경점수 높은 순',
    'university': '대학명 가나다순'
};

// Y축 범위 모드별 한글명
const Y_AXIS_MODE_NAMES = {
    'auto': '자동 조절',
    'dataRange': '데이터 범위 기준',
    'custom': '사용자 지정',
    'enhanced': '향상된 표시'
};

// CSV 파일 로드 (예측데이터총합.csv)
async function loadCSVData() {
    try {
        console.log('예측데이터총합.csv 파일 로딩 중...');
        
        // 단일 CSV 파일 경로
        const csvPath = `../../resource/csv_files/예측데이터총합.csv`;
        
        const response = await fetch(csvPath);
        if (!response.ok) {
            throw new Error(`CSV 파일을 찾을 수 없습니다: ${csvPath} (상태: ${response.status})`);
        }
        
        const csvText = await response.text();
        
        // CSV 파싱
        csvData = parseCSV(csvText);
        
        console.log('CSV 데이터 로드 완료:', csvData.length, '행');
        console.log('컬럼명:', Object.keys(csvData[0] || {}));
        
        // 사용 가능한 연도 추출
        extractAvailableYears();
        
        // 데이터 검증
        const validation = validateData(csvData);
        if (!validation.valid) {
            throw new Error(validation.message);
        }
        
        // 연도 셀렉트 박스 초기화
        initializeYearSelect();
        
        return csvData;
    } catch (error) {
        console.error('CSV 로드 실패:', error);
        showError(`예측데이터총합.csv 파일을 불러올 수 없습니다: ${error.message}`);
        return null;
    }
}

// 사용 가능한 연도 추출 (동적 범위 감지)
function extractAvailableYears() {
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
    
    // 연도 정렬 (내림차순 - 최신 연도부터)
    availableYears.sort((a, b) => b - a);
    
    console.log('CSV에서 감지된 사용 가능한 연도:', availableYears);
    console.log('연도 범위:', availableYears.length > 0 ? `${Math.min(...availableYears)} ~ ${Math.max(...availableYears)}` : '없음');
}

// 연도 셀렉트 박스 초기화
function initializeYearSelect() {
    const yearSelect = document.getElementById('yearSelect');
    if (!yearSelect) return;
    
    // 기존 옵션 제거
    yearSelect.innerHTML = '';
    
    // 사용 가능한 연도로 옵션 추가
    availableYears.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = `${year}년`;
        yearSelect.appendChild(option);
    });
    
    // 기본값을 가장 최신 연도로 설정
    if (availableYears.length > 0) {
        currentYear = availableYears[0];
        yearSelect.value = currentYear;
        updateCurrentInfo();
    }
}

// CSV 파싱 함수 (개선됨)
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

// **핵심: generateChart 함수 정의**
function generateChart() {
    console.log('차트 생성 함수 호출됨');
    generateChartFromCSV();
}

// CSV 데이터로 차트 생성 (수정됨)
async function generateChartFromCSV() {
    // CSV 데이터가 없으면 먼저 로드
    if (!csvData) {
        showLoading();
        await loadCSVData();
        if (!csvData) {
            hideLoading();
            return;
        }
        hideLoading();
    }
    
    const year = document.getElementById('yearSelect').value;
    currentYear = year;
    
    const chartTypeSelect = document.getElementById('chartType');
    const dataRangeSelect = document.getElementById('dataRange');
    
    const chartType = chartTypeSelect.value;
    const dataRange = dataRangeSelect.value;
    
    console.log('차트 생성 요청:', { year, chartType, dataRange });
    
    // 로딩 표시
    showLoading();
    
    try {
        // 데이터 처리 (연도별 컬럼 사용)
        const processedData = processCSVDataForChart(csvData, year, dataRange);
        
        if (processedData && processedData.length > 0) {
            // 차트 생성
            createChart(processedData, chartType);
            updateDataCount(processedData.length);
            
            // 통계 정보 표시
            const stats = calculateStatistics(processedData);
            if (stats) {
                console.log('통계 정보:', stats);
                console.log(`점수 범위: ${stats.min}점 ~ ${stats.max}점`);
            }
            
            // 플레이스홀더 숨기기
            document.getElementById('chartPlaceholder').style.display = 'none';
        } else {
            showError('선택한 조건에 해당하는 데이터가 없습니다.');
        }
    } catch (error) {
        console.error('차트 생성 실패:', error);
        showError('차트 생성 중 오류가 발생했습니다: ' + error.message);
    } finally {
        hideLoading();
    }
}

// CSV 데이터 처리 (연도별 컬럼 사용하도록 수정)
function processCSVDataForChart(data, selectedYear, dataRangeType) {
    // 1단계: 선택된 연도의 점수 컬럼명 생성
    const scoreColumn = `SCR_EST_${selectedYear}`;
    console.log(`선택된 연도: ${selectedYear}, 점수 컬럼: ${scoreColumn}`);
    
    // 2단계: 유효한 데이터만 필터링 (선택된 연도의 점수가 있는 데이터)
    let validData = data.filter(row => {
        const scoreValue = row[scoreColumn];
        return scoreValue !== null && 
               scoreValue !== undefined && 
               scoreValue !== '' &&
               scoreValue !== '-' &&
               !isNaN(parseFloat(scoreValue)) &&
               row['SNM']; // 학교명이 있어야 함
    });

    console.log('유효한 전체 데이터 수:', validData.length);

    // 전체 데이터를 점수 기준으로 정렬하여 전역 변수에 저장 (전체 순위 계산용)
    globalSortedData = [...validData].sort((a, b) => {
        const scoreA = parseFloat(a[scoreColumn]) || 0;
        const scoreB = parseFloat(b[scoreColumn]) || 0;
        return scoreB - scoreA; // 높은 점수부터 정렬
    });

    // 3단계: 필터 적용 (범위 선택 전에 먼저 적용)
    let filteredData = applyFilters(validData);
    console.log('필터 적용 후 데이터 수:', filteredData.length);

    // 4단계: 필터링된 데이터를 점수 기준으로 정렬 (높은 점수부터)
    filteredData.sort((a, b) => {
        const scoreA = parseFloat(a[scoreColumn]) || 0;
        const scoreB = parseFloat(b[scoreColumn]) || 0;
        return scoreB - scoreA; // 높은 점수부터 정렬
    });

    // 5단계: 데이터 범위에 따라 선택
    let selectedData = [];
    const topBottomCount = parseInt(document.getElementById('topBottomCount')?.value) || 10;
    const rangeStart = parseInt(document.getElementById('rangeStart')?.value) || 1;
    const rangeEnd = parseInt(document.getElementById('rangeEnd')?.value) || rangeStart;

    console.log('데이터 범위 설정:', { dataRangeType, topBottomCount, rangeStart, rangeEnd });
    console.log('필터링된 데이터 수:', filteredData.length);

    switch(dataRangeType) {
        case 'top':
            selectedData = filteredData.slice(0, Math.min(topBottomCount, filteredData.length));
            console.log(`상위 ${topBottomCount}개 선택됨 (실제: ${selectedData.length}개)`);
            break;
        case 'bottom':
            selectedData = filteredData.slice(-Math.min(topBottomCount, filteredData.length));
            console.log(`하위 ${topBottomCount}개 선택됨 (실제: ${selectedData.length}개)`);
            break;
        case 'range':
            // 순위는 1부터 시작하므로 인덱스 변환
            const startIndex = Math.max(1, rangeStart) - 1;  // 1순위 = 0번째 인덱스
            const endIndex = Math.min(filteredData.length, Math.max(rangeStart, rangeEnd));  // 끝 순위
            
            console.log(`범위 계산: ${rangeStart}위~${rangeEnd}위 -> 인덱스 ${startIndex}~${endIndex-1}`);
            console.log(`필터링된 데이터 수: ${filteredData.length}`);
            
            if (startIndex < filteredData.length && endIndex > startIndex) {
                selectedData = filteredData.slice(startIndex, endIndex);
                console.log(`${rangeStart}위~${rangeEnd}위 선택됨 (실제: ${selectedData.length}개)`);
                
                // 예상 개수와 실제 개수 비교
                const expectedCount = endIndex - startIndex;
                console.log(`예상 개수: ${expectedCount}개, 실제 개수: ${selectedData.length}개`);
            } else {
                console.log('잘못된 범위 설정 또는 데이터 부족');
                selectedData = [];
            }
            break;
        default: // 'all'
            selectedData = filteredData;
            console.log('전체 데이터 선택됨');
            break;
    }

    console.log('최종 선택된 데이터 수:', selectedData.length);

    // 6단계: 사용자가 선택한 정렬 방식 적용
    const sortOrder = document.getElementById('sortOrder').value;
    applySorting(selectedData, sortOrder, scoreColumn);

    // 7단계: 차트용 데이터 변환 (동적 순위 계산)
    return selectedData.map((row, index) => {
        const score = parseFloat(row[scoreColumn]) || 0;
        return {
            university: row['SNM'] || 'Unknown',
            value: score,
            styp: row['STYP'] || '',
            fnd: row['FND'] || '',
            rgn: row['RGN'] || '',
            usc: row['USC'] || '',
            rank: index + 1, // 현재 순위
            originalRank: getOriginalRank(row, globalSortedData, scoreColumn), // 전체에서의 원래 순위
            label: `${row['SNM']} (점수: ${score}, 전체 ${getOriginalRank(row, globalSortedData, scoreColumn)}위)`
        };
    });
}

// 전체 데이터에서의 원래 순위 구하기 (수정됨)
function getOriginalRank(targetRow, allSortedData, scoreColumn) {
    // 전체 데이터에서 동일한 학교 찾기
    for (let i = 0; i < allSortedData.length; i++) {
        if (allSortedData[i]['SNM'] === targetRow['SNM'] && 
            Math.abs(parseFloat(allSortedData[i][scoreColumn]) - parseFloat(targetRow[scoreColumn])) < 0.01) {
            return i + 1;
        }
    }
    return -1;
}

// 전체 데이터 정렬 상태를 저장할 전역 변수
let globalSortedData = null;

// 필터 적용 함수
function applyFilters(data) {
    const stypFilter = document.getElementById('stypFilter').value;
    const fndFilter = document.getElementById('fndFilter').value;
    const rgnFilter = document.getElementById('rgnFilter').value;
    const uscFilter = document.getElementById('uscFilter').value;
    
    console.log('적용된 필터:', { stypFilter, fndFilter, rgnFilter, uscFilter });
    
    return data.filter(row => {
        // 대학유형 필터
        if (stypFilter !== '전체' && row['STYP'] !== stypFilter) {
            return false;
        }
        
        // 설립 필터
        if (fndFilter !== '전체' && row['FND'] !== fndFilter) {
            return false;
        }
        
        // 지역 필터
        if (rgnFilter !== '전체' && row['RGN'] !== rgnFilter) {
            return false;
        }
        
        // 규모 필터
        if (uscFilter !== '전체') {
            if (uscFilter === '기타' && row['USC'] !== '-' && row['USC'] !== '' && row['USC'] !== null) {
                return false;
            } else if (uscFilter !== '기타' && row['USC'] !== uscFilter) {
                return false;
            }
        }
        
        return true;
    });
}

// 정렬 적용 함수 (연도별 점수 컬럼 사용)
function applySorting(data, sortOrder, scoreColumn) {
    switch(sortOrder) {
        case 'rank_asc':
            // 환경점수 오름차순 (낮은 점수부터)
            data.sort((a, b) => {
                const scoreA = parseFloat(a[scoreColumn]) || 0;
                const scoreB = parseFloat(b[scoreColumn]) || 0;
                return scoreA - scoreB;
            });
            break;
            
        case 'rank_desc':
            // 환경점수 내림차순 (높은 점수부터)
            data.sort((a, b) => {
                const scoreA = parseFloat(a[scoreColumn]) || 0;
                const scoreB = parseFloat(b[scoreColumn]) || 0;
                return scoreB - scoreA;
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

// Y축 범위 계산 함수
function calculateYAxisRange(data, mode) {
    if (!data || data.length === 0) {
        return { min: 0, max: 10 };
    }
    
    const values = data.map(item => item.value).filter(val => !isNaN(val));
    if (values.length === 0) {
        return { min: 0, max: 10 };
    }
    
    const dataMin = Math.min(...values);
    const dataMax = Math.max(...values);
    
    switch(mode) {
        case 'auto':
            // Chart.js 기본 자동 조절
            return { min: undefined, max: undefined };
            
        case 'dataRange':
            // 데이터의 실제 범위
            return { min: dataMin, max: dataMax };
            
        case 'custom':
            // 사용자 지정 범위
            const customMin = document.getElementById('yAxisMin').value;
            const customMax = document.getElementById('yAxisMax').value;
            return {
                min: customMin !== '' ? parseFloat(customMin) : dataMin,
                max: customMax !== '' ? parseFloat(customMax) : dataMax
            };
            
        case 'enhanced':
            // 향상된 표시 (약간의 여백 추가)
            const range = dataMax - dataMin;
            const padding = Math.max(range * 0.1, 0.5); // 최소 0.5의 여백
            return {
                min: Math.max(0, dataMin - padding),
                max: dataMax + padding
            };
            
        default:
            return { min: 0, max: 10 };
    }
}

// Y축 모드 변경 이벤트
function onYAxisModeChange() {
    const mode = document.getElementById('yAxisMode').value;
    const customRangeGroup = document.getElementById('customRangeGroup');
    const customRangeGroupMax = document.getElementById('customRangeGroupMax');
    
    // 사용자 지정 모드일 때만 입력 필드 표시
    if (mode === 'custom') {
        if (customRangeGroup) customRangeGroup.style.display = 'block';
        if (customRangeGroupMax) customRangeGroupMax.style.display = 'block';
        
        // 현재 데이터 범위를 기본값으로 설정
        if (chartData && chartData.length > 0) {
            const values = chartData.map(item => item.value).filter(val => !isNaN(val));
            if (values.length > 0) {
                const dataMin = Math.min(...values);
                const dataMax = Math.max(...values);
                const yAxisMinInput = document.getElementById('yAxisMin');
                const yAxisMaxInput = document.getElementById('yAxisMax');
                if (yAxisMinInput) yAxisMinInput.value = dataMin;
                if (yAxisMaxInput) yAxisMaxInput.value = dataMax;
            }
        }
    } else {
        if (customRangeGroup) customRangeGroup.style.display = 'none';
        if (customRangeGroupMax) customRangeGroupMax.style.display = 'none';
    }
    
    updateCurrentInfo();
    
    // 차트가 있다면 새로운 Y축 설정으로 다시 생성
    if (currentChart && chartData) {
        const chartType = document.getElementById('chartType').value;
        createChart(chartData, chartType);
    }
}

// 사용자 지정 범위 변경 이벤트
function onCustomRangeChange() {
    const mode = document.getElementById('yAxisMode').value;
    if (mode === 'custom' && currentChart && chartData) {
        const chartType = document.getElementById('chartType').value;
        createChart(chartData, chartType);
    }
}

// Chart.js를 사용한 차트 생성
function createChart(data, chartType) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // 기존 차트 제거
    if (currentChart) {
        currentChart.destroy();
    }
    
    chartData = data;
    
    const labels = data.map(item => item.university);
    const values = data.map(item => item.value);
    
    const chartConfig = {
        type: chartType === 'scatter' ? 'scatter' : chartType,
        data: {
            labels: labels,
            datasets: [{
                label: '환경점수',
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
                    text: `환경점수 분석 (${currentYear}년)`,
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
            scales: getScaleConfig(chartType),
            elements: {
                point: {
                    radius: chartType === 'scatter' ? 6 : 3,
                    hoverRadius: 8
                }
            }
        }
    };
    
    currentChart = new Chart(ctx, chartConfig);
    console.log('차트 생성 완료');
}

// 차트 타입별 스케일 설정 (Y축 범위 조절 기능 포함)
function getScaleConfig(chartType) {
    if (chartType === 'pie') {
        return {};
    }
    
    // Y축 범위 설정
    const yAxisMode = document.getElementById('yAxisMode')?.value || 'auto';
    const yAxisRange = calculateYAxisRange(chartData, yAxisMode);
    
    const scaleConfig = {
        x: {
            display: true,
            title: {
                display: true,
                text: '대학교',
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
                text: '환경점수',
                color: '#666'
            },
            beginAtZero: yAxisRange.min === undefined ? true : false
        }
    };
    
    // Y축 범위 설정 적용
    if (yAxisRange.min !== undefined) {
        scaleConfig.y.min = yAxisRange.min;
    }
    if (yAxisRange.max !== undefined) {
        scaleConfig.y.max = yAxisRange.max;
    }
    
    // 향상된 표시 모드에서는 틱 간격 조정
    if (yAxisMode === 'enhanced' && yAxisRange.min !== undefined && yAxisRange.max !== undefined) {
        const range = yAxisRange.max - yAxisRange.min;
        const stepSize = range / 8; // 8개 정도의 틱
        scaleConfig.y.ticks = {
            stepSize: Math.max(stepSize, 0.1),
            callback: function(value) {
                return Number(value).toFixed(1);
            }
        };
    }
    
    return scaleConfig;
}

// 평균값 데이터로 차트 업데이트
function updateChartWithAverageData() {
    if (!chartData) {
        console.log('차트 데이터가 없습니다.');
        return;
    }
    
    // 대학유형별 평균 계산
    const avgByType = {};
    const avgByFnd = {};
    const avgByRgn = {};
    const avgByUsc = {};
    
    chartData.forEach(item => {
        // 대학유형별
        if (item.styp && item.styp !== '') {
            if (!avgByType[item.styp]) avgByType[item.styp] = [];
            avgByType[item.styp].push(item.value);
        }
        
        // 설립별
        if (item.fnd && item.fnd !== '') {
            if (!avgByFnd[item.fnd]) avgByFnd[item.fnd] = [];
            avgByFnd[item.fnd].push(item.value);
        }
        
        // 지역별
        if (item.rgn && item.rgn !== '') {
            if (!avgByRgn[item.rgn]) avgByRgn[item.rgn] = [];
            avgByRgn[item.rgn].push(item.value);
        }
        
        // 규모별
        if (item.usc && item.usc !== '') {
            if (!avgByUsc[item.usc]) avgByUsc[item.usc] = [];
            avgByUsc[item.usc].push(item.value);
        }
    });
    
    // 대학유형별 평균으로 차트 생성
    const avgData = Object.keys(avgByType).map(type => ({
        university: type,
        value: avgByType[type].reduce((a, b) => a + b, 0) / avgByType[type].length,
        label: `${type} (평균: ${Math.round((avgByType[type].reduce((a, b) => a + b, 0) / avgByType[type].length) * 100) / 100})`,
        styp: type,
        fnd: '',
        rgn: '',
        usc: ''
    }));
    
    // 평균값 기준으로 정렬
    avgData.sort((a, b) => b.value - a.value);
    
    const chartType = document.getElementById('chartType').value;
    createChart(avgData, chartType);
}

// 데이터 검증 함수 (연도별 컬럼 확인)
function validateData(data) {
    if (!data || data.length === 0) {
        return { valid: false, message: '데이터가 없습니다.' };
    }
    
    const requiredColumns = ['SNM', 'STYP', 'FND', 'RGN', 'USC'];
    const availableColumns = Object.keys(data[0] || {});
    
    console.log('사용 가능한 컬럼:', availableColumns);
    console.log('필요한 컬럼:', requiredColumns);
    
    const missingColumns = requiredColumns.filter(col => !availableColumns.includes(col));
    if (missingColumns.length > 0) {
        return { 
            valid: false, 
            message: `필수 컬럼이 누락되었습니다: ${missingColumns.join(', ')}` 
        };
    }
    
    // 연도별 점수 컬럼이 하나 이상 있는지 확인
    const scoreColumns = availableColumns.filter(col => col.match(/^SCR_EST_\d{4}$/));
    if (scoreColumns.length === 0) {
        return {
            valid: false,
            message: 'SCR_EST_YYYY 형태의 점수 컬럼이 없습니다.'
        };
    }
    
    return { valid: true };
}

// 이벤트 핸들러 함수들
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
            window.location.href = 'page_mainpage_num01.html';
            break;
        default:
            alert('페이지를 찾을 수 없습니다.');
    }
}

function onYearChange() {
    const year = document.getElementById('yearSelect').value;
    console.log('연도 변경:', year);
    currentYear = year;
    
    updateCurrentInfo();
    
    // 차트가 있다면 새로운 연도로 다시 생성
    if (currentChart || csvData) {
        generateChartFromCSV();
    }
}

function onFilterChange() {
    console.log('필터 변경');
    updateCurrentInfo();
    
    // 차트가 있다면 새로운 필터로 다시 생성
    if (currentChart && csvData) {
        generateChartFromCSV();
    }
}

function onChartTypeChange() {
    updateCurrentInfo();
    if (currentChart && chartData) {
        const chartType = document.getElementById('chartType').value;
        createChart(chartData, chartType);
    }
}

// 데이터 범위 변경 이벤트 (수정됨 - 검증 추가)
function onDataRangeChange() {
    const dataRange = document.getElementById('dataRange').value;
    const topBottomCountGroup = document.getElementById('topBottomCountGroup');
    const rangeGroup = document.getElementById('rangeGroup');
    const rangeGroupEnd = document.getElementById('rangeGroupEnd');
    
    // 모든 그룹 숨기기
    if (topBottomCountGroup) topBottomCountGroup.style.display = 'none';
    if (rangeGroup) rangeGroup.style.display = 'none';
    if (rangeGroupEnd) rangeGroupEnd.style.display = 'none';
    
    // 선택된 범위에 따라 해당 입력 필드 표시
    switch(dataRange) {
        case 'top':
        case 'bottom':
            if (topBottomCountGroup) topBottomCountGroup.style.display = 'block';
            break;
        case 'range':
            if (rangeGroup) rangeGroup.style.display = 'block';
            if (rangeGroupEnd) rangeGroupEnd.style.display = 'block';
            
            // 범위 입력 시 기본값 설정
            const rangeStartInput = document.getElementById('rangeStart');
            const rangeEndInput = document.getElementById('rangeEnd');
            if (rangeStartInput && !rangeStartInput.value) {
                rangeStartInput.value = '1';
            }
            if (rangeEndInput && !rangeEndInput.value) {
                rangeEndInput.value = '50';
            }
            break;
        // 'all'은 추가 입력 필드 없음
    }
    
    // 범위 검증 (range 모드일 때만)
    if (dataRange === 'range') {
        validateRangeInputs();
    }
    
    // 차트가 있다면 새로운 범위로 다시 생성
    if (currentChart && csvData) {
        generateChartFromCSV();
    }
}

// 범위 입력 검증 함수
function validateRangeInputs() {
    const rangeStart = parseInt(document.getElementById('rangeStart')?.value) || 1;
    const rangeEnd = parseInt(document.getElementById('rangeEnd')?.value) || 50;
    
    if (rangeStart < 1) {
        document.getElementById('rangeStart').value = '1';
        console.log('시작 순위는 1 이상이어야 합니다.');
    }
    
    if (rangeEnd < rangeStart) {
        document.getElementById('rangeEnd').value = rangeStart;
        console.log('끝 순위는 시작 순위보다 크거나 같아야 합니다.');
    }
    
    // 예상 데이터 개수 계산
    const expectedCount = rangeEnd - rangeStart + 1;
    console.log(`예상 데이터 개수: ${expectedCount}개 (${rangeStart}위~${rangeEnd}위)`);
}

function onSortOrderChange() {
    console.log('정렬 방식 변경');
    updateCurrentInfo();
    
    if (currentChart && csvData) {
        generateChartFromCSV();
    }
}

function switchTab(tabName) {
    const tabs = document.querySelectorAll('.chart-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    event.target.classList.add('active');
    
    console.log('탭 전환:', tabName);
    
    if (tabName === 'table2') {
        updateChartWithAverageData();
    } else {
        if (csvData) {
            generateChartFromCSV();
        }
    }
}

function updateCurrentInfo() {
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = currentYear ? `${currentYear}년` : '-';
    }
    
    document.getElementById('currentStyp').textContent = document.getElementById('stypFilter').value;
    document.getElementById('currentFnd').textContent = document.getElementById('fndFilter').value;
    document.getElementById('currentRgn').textContent = document.getElementById('rgnFilter').value;
    document.getElementById('currentUsc').textContent = document.getElementById('uscFilter').value;
    document.getElementById('currentChartType').textContent = CHART_TYPE_NAMES[document.getElementById('chartType').value];
    document.getElementById('currentSortOrder').textContent = SORT_ORDER_NAMES[document.getElementById('sortOrder').value];
    
    // Y축 범위 정보 추가 (안전하게 처리)
    const yAxisModeElement = document.getElementById('yAxisMode');
    const yAxisInfoElement = document.getElementById('currentYAxisMode');
    if (yAxisModeElement && yAxisInfoElement) {
        const yAxisMode = yAxisModeElement.value || 'enhanced';
        yAxisInfoElement.textContent = Y_AXIS_MODE_NAMES[yAxisMode] || '향상된 표시';
    }
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
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                파일 경로를 확인하세요: ../../resource/csv_files/예측데이터총합.csv
            </p>
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
        const year = currentYear || 'unknown';
        const filters = `${document.getElementById('stypFilter').value}_${document.getElementById('fndFilter').value}_${document.getElementById('rgnFilter').value}_${document.getElementById('uscFilter').value}`;
        a.download = `libra_environment_chart_${year}_${filters}_${new Date().getTime()}.png`;
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
        year: currentYear || 'unknown',
        styp: document.getElementById('stypFilter').value,
        fnd: document.getElementById('fndFilter').value,
        rgn: document.getElementById('rgnFilter').value,
        usc: document.getElementById('uscFilter').value,
        chartType: document.getElementById('chartType').value,
        sortOrder: document.getElementById('sortOrder').value,
        dataRange: document.getElementById('dataRange').value,
        timestamp: new Date().toISOString()
    };
    
    const savedAnalyses = JSON.parse(localStorage.getItem('libra_environment_analyses') || '[]');
    savedAnalyses.push(currentConfig);
    localStorage.setItem('libra_environment_analyses', JSON.stringify(savedAnalyses));
    
    alert('현재 분석 설정이 즐겨찾기에 저장되었습니다.');
    console.log('분석 저장 완료:', currentConfig);
}

// 통계 정보 계산
function calculateStatistics(data) {
    if (!data || data.length === 0) return null;
    
    const scores = data.map(item => item.value).filter(val => !isNaN(val));
    
    if (scores.length === 0) return null;
    
    const sorted = [...scores].sort((a, b) => a - b);
    const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
    const median = sorted.length % 2 === 0 
        ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
        : sorted[Math.floor(sorted.length / 2)];
    
    return {
        count: scores.length,
        mean: Math.round(mean * 100) / 100,
        median: Math.round(median * 100) / 100,
        min: Math.min(...scores),
        max: Math.max(...scores)
    };
}

// 페이지 초기화
function initializePage() {
    console.log('환경점수예측 분석 페이지 초기화');
    
    // 기본 CSV 데이터 로드
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

// 필터 상태 저장/복원
function saveFilterState() {
    try {
        const filterState = {
            year: currentYear || 'unknown',
            styp: document.getElementById('stypFilter')?.value || '전체',
            fnd: document.getElementById('fndFilter')?.value || '전체',
            rgn: document.getElementById('rgnFilter')?.value || '전체',
            usc: document.getElementById('uscFilter')?.value || '전체',
            chartType: document.getElementById('chartType')?.value || 'bar',
            sortOrder: document.getElementById('sortOrder')?.value || 'rank_desc',
            dataRange: document.getElementById('dataRange')?.value || 'all',
            topBottomCount: document.getElementById('topBottomCount')?.value || '10',
            rangeStart: document.getElementById('rangeStart')?.value || '',
            rangeEnd: document.getElementById('rangeEnd')?.value || '',
            yAxisMode: document.getElementById('yAxisMode')?.value || 'enhanced',
            yAxisMin: document.getElementById('yAxisMin')?.value || '',
            yAxisMax: document.getElementById('yAxisMax')?.value || ''
        };
        
        localStorage.setItem('libra_environment_filter_state', JSON.stringify(filterState));
    } catch (error) {
        console.error('필터 상태 저장 실패:', error);
    }
}

function restoreFilterState() {
    const savedState = localStorage.getItem('libra_environment_filter_state');
    if (savedState) {
        try {
            const filterState = JSON.parse(savedState);
            
            // 연도는 사용 가능한 연도 중에서만 선택
            if (filterState.year && availableYears.includes(parseInt(filterState.year))) {
                currentYear = filterState.year;
                const yearSelect = document.getElementById('yearSelect');
                if (yearSelect) {
                    yearSelect.value = filterState.year;
                }
            }
            
            // 나머지 필터 상태 복원
            Object.keys(filterState).forEach(key => {
                if (key === 'year') return; // 연도는 이미 처리함
                
                const elementId = key === 'chartType' ? 'chartType' : 
                                key === 'sortOrder' ? 'sortOrder' : 
                                key === 'dataRange' ? 'dataRange' : 
                                key === 'topBottomCount' ? 'topBottomCount' :
                                key === 'rangeStart' ? 'rangeStart' :
                                key === 'rangeEnd' ? 'rangeEnd' :
                                key === 'yAxisMode' ? 'yAxisMode' :
                                key === 'yAxisMin' ? 'yAxisMin' :
                                key === 'yAxisMax' ? 'yAxisMax' :
                                key + 'Filter';
                const element = document.getElementById(elementId);
                if (element && filterState[key] !== undefined) {
                    element.value = filterState[key];
                }
            });
            
            // 데이터 범위에 따라 입력 필드 표시/숨김
            if (filterState.dataRange && typeof onDataRangeChange === 'function') {
                onDataRangeChange();
            }
            
            // Y축 모드에 따라 사용자 지정 입력 필드 표시/숨김
            if (filterState.yAxisMode && typeof onYAxisModeChange === 'function') {
                onYAxisModeChange();
            }
            
            console.log('필터 상태 복원 완료:', filterState);
        } catch (error) {
            console.error('필터 상태 복원 실패:', error);
        }
    }
}

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        generateChart();
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
window.addEventListener('load', function() {
    initializePage();
    
    // CSV 로드 완료 후 필터 상태 복원
    setTimeout(() => {
        restoreFilterState();
        updateCurrentInfo();
    }, 500);
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('환경점수예측 분석 페이지 DOM 로드 완료');
    
    // DOM이 로드된 후에도 초기화 시도
    if (document.readyState === 'complete') {
        initializePage();
    }
});

// 페이지 떠날 때 필터 상태 저장
window.addEventListener('beforeunload', function() {
    saveFilterState();
    
    if (currentChart) {
        currentChart.destroy();
    }
    console.log('환경점수예측 분석 페이지를 떠납니다.');
});

// 디버깅용 함수
function debugInfo() {
    console.log('=== 디버깅 정보 ===');
    console.log('현재 연도:', currentYear);
    console.log('사용 가능한 연도:', availableYears);
    console.log('CSV 데이터:', csvData ? csvData.length + '행' : '없음');
    console.log('차트 데이터:', chartData ? chartData.length + '개' : '없음');
    console.log('현재 차트:', currentChart ? '있음' : '없음');
    
    if (csvData && csvData.length > 0) {
        console.log('컬럼명:', Object.keys(csvData[0]));
        console.log('첫 번째 행:', csvData[0]);
        
        // 점수 컬럼들 확인
        const scoreColumns = Object.keys(csvData[0]).filter(key => key.match(/^SCR_EST_\d{4}$/));
        console.log('점수 컬럼들:', scoreColumns);
        
        // 현재 연도 점수 샘플 값들
        if (currentYear) {
            const currentScoreColumn = `SCR_EST_${currentYear}`;
            const scoreValues = csvData.slice(0, 5).map(row => row[currentScoreColumn]);
            console.log(`${currentScoreColumn} 샘플 값들:`, scoreValues);
        }
    }
    
    // 현재 필터 상태
    console.log('현재 필터 상태:', {
        year: currentYear,
        styp: document.getElementById('stypFilter')?.value,
        fnd: document.getElementById('fndFilter')?.value,
        rgn: document.getElementById('rgnFilter')?.value,
        usc: document.getElementById('uscFilter')?.value
    });
}

// 개발자 도구용 전역 함수 등록
window.debugInfo = debugInfo;
window.libra = {
    csvData,
    chartData,
    currentChart,
    currentYear,
    availableYears,
    generateChart,
    loadData: loadCSVData,
    debugInfo,
    // 추가 디버깅 함수들
    testFilters: function() {
        if (csvData) {
            console.log('전체 데이터 수:', csvData.length);
            console.log('필터 적용 후:', applyFilters(csvData).length);
        }
    },
    showCSVStructure: function() {
        if (csvData && csvData.length > 0) {
            console.log('CSV 구조 분석:');
            const firstRow = csvData[0];
            Object.keys(firstRow).forEach(key => {
                const sampleValues = csvData.slice(0, 3).map(row => row[key]);
                console.log(`${key}:`, sampleValues);
            });
        }
    },
    testYearColumn: function(year) {
        if (csvData && year) {
            const scoreColumn = `SCR_EST_${year}`;
            console.log(`${scoreColumn} 테스트:`);
            const validData = csvData.filter(row => {
                const score = row[scoreColumn];
                return score !== null && score !== undefined && score !== '' && !isNaN(parseFloat(score));
            });
            console.log(`유효한 데이터 수: ${validData.length}개`);
            if (validData.length > 0) {
                const scores = validData.map(row => parseFloat(row[scoreColumn]));
                console.log(`점수 범위: ${Math.min(...scores)} ~ ${Math.max(...scores)}`);
            }
        }
    },
    // 모든 연도별 데이터 현황 확인
    checkAllYearData: function() {
        if (!csvData || csvData.length === 0) {
            console.log('CSV 데이터가 없습니다.');
            return;
        }
        
        console.log('=== 전체 연도별 데이터 현황 ===');
        availableYears.forEach(year => {
            const scoreColumn = `SCR_EST_${year}`;
            const validCount = csvData.filter(row => {
                const score = row[scoreColumn];
                return score !== null && score !== undefined && score !== '' && !isNaN(parseFloat(score));
            }).length;
            
            console.log(`${year}년: ${validCount}개 유효 데이터 (전체 ${csvData.length}개 중)`);
        });
        
        // 빈 데이터가 있는 연도들 확인
        const emptyYears = availableYears.filter(year => {
            const scoreColumn = `SCR_EST_${year}`;
            const validCount = csvData.filter(row => {
                const score = row[scoreColumn];
                return score !== null && score !== undefined && score !== '' && !isNaN(parseFloat(score));
            }).length;
            return validCount === 0;
        });
        
        if (emptyYears.length > 0) {
            console.warn('데이터가 없는 연도들:', emptyYears);
        }
    },
    // CSV 컬럼 구조 상세 분석
    analyzeCSVStructure: function() {
        if (!csvData || csvData.length === 0) {
            console.log('CSV 데이터가 없습니다.');
            return;
        }
        
        const firstRow = csvData[0];
        const allColumns = Object.keys(firstRow);
        
        console.log('=== CSV 컬럼 구조 분석 ===');
        console.log('총 컬럼 수:', allColumns.length);
        
        // 기본 정보 컬럼들
        const basicColumns = allColumns.filter(col => !col.match(/^SCR_EST_\d{4}$/));
        console.log('기본 정보 컬럼들:', basicColumns);
        
        // 점수 컬럼들 (연도별)
        const scoreColumns = allColumns.filter(col => col.match(/^SCR_EST_\d{4}$/));
        console.log('점수 컬럼들:', scoreColumns.sort());
        
        // 각 컬럼의 샘플 데이터
        console.log('\n=== 컬럼별 샘플 데이터 ===');
        allColumns.forEach(col => {
            const sampleValues = csvData.slice(0, 3).map(row => row[col]);
            console.log(`${col}:`, sampleValues);
        });
    }
};