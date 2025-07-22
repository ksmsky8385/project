// 유저 환경점수 분석 스크립트
// 파일명: script_userpage_num01.js

// 전역 변수
let userDataCSV = null;
let yearlyDataCache = {};
let predictionDataCSV = null;
let currentUserData = null;
let analysisCharts = [];

// 차트 색상
const USER_COLOR = '#42a5f5';
const UNIVERSITY_COLOR = '#29b6f6';
const SIMILAR_COLORS = ['#81c784', '#ffb74d', '#ff8a65', '#ba68c8'];

// 데이터 타입 매핑
const DATA_TYPES = {
    'CPS': { key: 'USR_CPS', univKey: 'CPSS_CPS', label: '자료구입비' },
    'LPS': { key: 'USR_LPS', univKey: 'LPS_LPS', label: '대출책수' },
    'VPS': { key: 'USR_VPS', univKey: 'VPS_VPS', label: '도서관방문수' }
};

// CSV 파싱 함수
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) {
        throw new Error('CSV 파일이 비어있거나 형식이 올바르지 않습니다.');
    }
    
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length === headers.length) {
            const row = {};
            headers.forEach((header, index) => {
                const value = values[index];
                const numValue = parseFloat(value);
                row[header] = isNaN(numValue) ? value : numValue;
            });
            data.push(row);
        }
    }
    
    return data;
}

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

// 유저 데이터 로드
async function loadUserData() {
    try {
        console.log('유저환경점수.csv 파일 로딩 중...');
        
        const csvPath = `../../resource/csv_files/유저환경점수.csv`;
        const response = await fetch(csvPath);
        
        if (!response.ok) {
            throw new Error(`CSV 파일을 찾을 수 없습니다: ${csvPath} (상태: ${response.status})`);
        }
        
        const csvText = await response.text();
        userDataCSV = parseCSV(csvText);
        
        console.log('유저 데이터 로드 완료:', userDataCSV.length, '명');
        
        // 유저 선택 박스 초기화
        initializeUserSelect();
        
        return userDataCSV;
    } catch (error) {
        console.error('유저 데이터 로드 실패:', error);
        showError(`유저환경점수.csv 파일을 불러올 수 없습니다: ${error.message}`);
        return null;
    }
}

// 연도별 데이터 로드
async function loadYearlyData(year) {
    if (yearlyDataCache[year]) {
        return yearlyDataCache[year];
    }
    
    try {
        const csvPath = `../../resource/csv_files/csv_data/Num06_종합데이터_${year}.csv`;
        const response = await fetch(csvPath);
        
        if (!response.ok) {
            throw new Error(`${year}년 데이터 파일을 찾을 수 없습니다: ${csvPath}`);
        }
        
        const csvText = await response.text();
        const data = parseCSV(csvText);
        
        yearlyDataCache[year] = data;
        console.log(`${year}년 데이터 로드 완료:`, data.length, '행');
        
        return data;
    } catch (error) {
        console.error(`${year}년 데이터 로드 실패:`, error);
        return null;
    }
}

// 예측 데이터 로드
async function loadPredictionData() {
    if (predictionDataCSV) {
        return predictionDataCSV;
    }
    
    try {
        console.log('예측데이터총합.csv 파일 로딩 중...');
        
        const csvPath = `../../resource/csv_files/예측데이터총합.csv`;
        const response = await fetch(csvPath);
        
        if (!response.ok) {
            throw new Error(`예측데이터총합.csv 파일을 찾을 수 없습니다: ${csvPath}`);
        }
        
        const csvText = await response.text();
        predictionDataCSV = parseCSV(csvText);
        
        console.log('예측 데이터 로드 완료:', predictionDataCSV.length, '행');
        
        return predictionDataCSV;
    } catch (error) {
        console.error('예측 데이터 로드 실패:', error);
        showError(`예측데이터총합.csv 파일을 불러올 수 없습니다: ${error.message}`);
        return null;
    }
}

// 유저 선택 박스 초기화
function initializeUserSelect() {
    const userSelect = document.getElementById('userSelect');
    if (!userSelect || !userDataCSV) return;
    
    userSelect.innerHTML = '<option value="">유저를 선택하세요</option>';
    
    userDataCSV.forEach((user, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${user.USR_NAME} (${user.USR_SNM})`;
        userSelect.appendChild(option);
    });
}

// 유저 변경 이벤트
function onUserChange() {
    const userSelect = document.getElementById('userSelect');
    const selectedIndex = userSelect.value;
    
    if (selectedIndex === '') {
        clearUserInfo();
        return;
    }
    
    currentUserData = userDataCSV[selectedIndex];
    updateUserInfo(currentUserData);
    console.log('선택된 유저:', currentUserData);
}

// 유저 정보 업데이트
function updateUserInfo(userData) {
    document.getElementById('selectedUserName').textContent = userData.USR_NAME || '-';
    document.getElementById('selectedUserUniv').textContent = userData.USR_SNM || '-';
    
    document.getElementById('year1st').textContent = userData['1ST_YR'] || '-';
    document.getElementById('year2nd').textContent = userData['2ND_YR'] || '-';
    document.getElementById('year3rd').textContent = userData['3RD_YR'] || '-';
    document.getElementById('year4th').textContent = userData['4TH_YR'] || '-';
}

// 유저 정보 초기화
function clearUserInfo() {
    document.getElementById('selectedUserName').textContent = '-';
    document.getElementById('selectedUserUniv').textContent = '-';
    
    document.getElementById('year1st').textContent = '-';
    document.getElementById('year2nd').textContent = '-';
    document.getElementById('year3rd').textContent = '-';
    document.getElementById('year4th').textContent = '-';
    
    currentUserData = null;
}

// 유저 분석 시작
async function generateUserAnalysis() {
    if (!currentUserData) {
        showError('유저를 먼저 선택해주세요.');
        return;
    }
    
    showLoading();
    
    try {
        // 예측 데이터 로드
        await loadPredictionData();
        
        // 분석 데이터 생성
        const analysisData = await createAnalysisData(currentUserData);
        
        // 차트 생성
        await createAllCharts(analysisData);
        
        console.log('유저 분석 완료');
        
    } catch (error) {
        console.error('유저 분석 실패:', error);
        showError('분석 중 오류가 발생했습니다: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 분석 데이터 생성
async function createAnalysisData(userData) {
    const analysisData = {
        user: userData,
        grades: {}
    };
    
    // 각 학년별 데이터 처리
    for (let grade = 1; grade <= 4; grade++) {
        const gradeKey = `${grade === 1 ? '1ST' : grade === 2 ? '2ND' : grade === 3 ? '3RD' : '4TH'}`;
        const year = userData[`${gradeKey}_YR`];
        
        if (!year || year === '-' || year === '') {
            console.log(`${grade}학년 연도 정보가 없습니다.`);
            continue;
        }
        
        console.log(`${grade}학년 (${year}년) 데이터 처리 중...`);
        
        // 해당 연도 데이터 로드
        const yearlyData = await loadYearlyData(year);
        if (!yearlyData) {
            console.error(`${year}년 데이터를 로드할 수 없습니다.`);
            continue;
        }
        
        // 유저의 소속대학 데이터 찾기
        const universityData = yearlyData.find(row => row.SNM === userData.USR_SNM);
        if (!universityData) {
            console.error(`${year}년 데이터에서 ${userData.USR_SNM} 대학을 찾을 수 없습니다.`);
            continue;
        }
        
        // 유저 환경점수와 대학 환경점수 추출
        const userScore = userData[`SCR_EST_${gradeKey}`];
        const universityScore = await getUniversityScore(userData.USR_SNM, year);
        
        // 유사 점수 대학들 찾기
        const similarUniversities = await findSimilarUniversities(userScore, year);
        
        analysisData.grades[grade] = {
            year: year,
            userData: {
                CPS: userData[`${gradeKey}_USR_CPS`],
                LPS: userData[`${gradeKey}_USR_LPS`],
                VPS: userData[`${gradeKey}_USR_VPS`]
            },
            universityData: {
                CPS: universityData.CPSS_CPS,
                LPS: universityData.LPS_LPS,
                VPS: universityData.VPS_VPS
            },
            userScore: userScore,
            universityScore: universityScore,
            similarUniversities: similarUniversities
        };
    }
    
    console.log('분석 데이터 생성 완료:', analysisData);
    return analysisData;
}

// 대학 환경점수 가져오기
async function getUniversityScore(universityName, year) {
    if (!predictionDataCSV) {
        await loadPredictionData();
    }
    
    const scoreColumn = `SCR_EST_${year}`;
    const universityData = predictionDataCSV.find(row => row.SNM === universityName);
    
    if (universityData && universityData[scoreColumn] !== undefined) {
        return universityData[scoreColumn];
    }
    
    console.warn(`${universityName}의 ${year}년 환경점수를 찾을 수 없습니다.`);
    return null;
}

// 유사 점수 대학 찾기 (정확한 ±1,±2등 추출)
async function findSimilarUniversities(userScore, year) {
    if (!predictionDataCSV || !userScore) {
        console.log('예측 데이터 또는 유저 점수가 없습니다.');
        return [];
    }
    
    const scoreColumn = `SCR_EST_${year}`;
    const userScoreFloat = parseFloat(userScore);
    
    console.log(`=== 유사 점수 대학 찾기 (${year}년, 유저 점수: ${userScore}) ===`);
    
    // 해당 연도에 점수가 있는 대학들만 필터링
    const validUniversities = predictionDataCSV.filter(row => {
        const score = row[scoreColumn];
        return score !== null && 
               score !== undefined && 
               score !== '' &&
               !isNaN(parseFloat(score));
    });
    
    console.log(`유효한 대학 수: ${validUniversities.length}개`);
    
    // 점수로 내림차순 정렬 (높은 점수부터)
    validUniversities.sort((a, b) => parseFloat(b[scoreColumn]) - parseFloat(a[scoreColumn]));
    
    // 유저 점수가 들어갈 순위 찾기 (내림차순에서)
    let userRank = validUniversities.length; // 기본값: 최하위
    
    for (let i = 0; i < validUniversities.length; i++) {
        const univScore = parseFloat(validUniversities[i][scoreColumn]);
        if (univScore <= userScoreFloat) {
            userRank = i;
            break;
        }
    }
    
    console.log(`유저는 전체 ${userRank + 1}위 (${validUniversities.length}개 대학 중)`);
    
    // 정확히 ±1등, ±2등 추출
    const result = {
        minus2: null,  // -2등 (유저보다 2등 낮음)
        minus1: null,  // -1등 (유저보다 1등 낮음)  
        plus1: null,   // +1등 (유저보다 1등 높음)
        plus2: null    // +2등 (유저보다 2등 높음)
    };
    
    // -2등 (유저 순위 + 2)
    if (userRank + 2 < validUniversities.length) {
        const univ = validUniversities[userRank + 2];
        result.minus2 = {
            name: univ.SNM,
            score: parseFloat(univ[scoreColumn]),
            rank: userRank + 3, // +2등이므로 순위는 +2
            position: 'minus2'
        };
    }
    
    // -1등 (유저 순위 + 1)  
    if (userRank + 1 < validUniversities.length) {
        const univ = validUniversities[userRank + 1];
        result.minus1 = {
            name: univ.SNM,
            score: parseFloat(univ[scoreColumn]),
            rank: userRank + 2, // +1등이므로 순위는 +1
            position: 'minus1'
        };
    }
    
    // +1등 (유저 순위 - 1)
    if (userRank - 1 >= 0) {
        const univ = validUniversities[userRank - 1];
        result.plus1 = {
            name: univ.SNM,
            score: parseFloat(univ[scoreColumn]),
            rank: userRank, // -1등이므로 순위는 -1
            position: 'plus1'
        };
    }
    
    // +2등 (유저 순위 - 2)
    if (userRank - 2 >= 0) {
        const univ = validUniversities[userRank - 2];
        result.plus2 = {
            name: univ.SNM,
            score: parseFloat(univ[scoreColumn]),
            rank: userRank - 1, // -2등이므로 순위는 -2  
            position: 'plus2'
        };
    }
    
    // null이 아닌 결과만 배열로 변환
    const finalResult = [];
    if (result.minus2) finalResult.push(result.minus2);
    if (result.minus1) finalResult.push(result.minus1);  
    if (result.plus1) finalResult.push(result.plus1);
    if (result.plus2) finalResult.push(result.plus2);
    
    console.log('추출된 유사 대학들:');
    console.log('  +2등:', result.plus2 ? `${result.plus2.name} (${result.plus2.score})` : '없음');
    console.log('  +1등:', result.plus1 ? `${result.plus1.name} (${result.plus1.score})` : '없음'); 
    console.log('  유저:', `${userScore}점`);
    console.log('  -1등:', result.minus1 ? `${result.minus1.name} (${result.minus1.score})` : '없음');
    console.log('  -2등:', result.minus2 ? `${result.minus2.name} (${result.minus2.score})` : '없음');
    
    return finalResult;
}

// 모든 차트 생성
async function createAllCharts(analysisData) {
    // 기존 차트 제거
    analysisCharts.forEach(chart => {
        if (chart) chart.destroy();
    });
    analysisCharts = [];
    
    const chartGrid = document.getElementById('chartGrid');
    const placeholder = document.getElementById('chartPlaceholder');
    
    // 플레이스홀더 숨기기
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    
    // 차트 그리드 초기화
    chartGrid.innerHTML = '';
    
    // 1-4번 블록: 학년별 3개 데이터 + 도넛 차트
    for (let grade = 1; grade <= 4; grade++) {
        if (analysisData.grades[grade]) {
            await createGradeComparisonBlock(chartGrid, grade, analysisData.grades[grade]);
        }
    }
    
    // 5-8번 블록: 환경점수 비교
    for (let grade = 1; grade <= 4; grade++) {
        if (analysisData.grades[grade]) {
            await createScoreComparisonBlock(chartGrid, grade, analysisData.grades[grade]);
        }
    }
}

// 학년별 비교 블록 생성 (개별 막대 + 도넛 차트)
async function createGradeComparisonBlock(container, grade, gradeData) {
    const blockDiv = document.createElement('div');
    blockDiv.className = 'chart-block';
    
    blockDiv.innerHTML = `
        <div class="chart-block-header">
            ${grade}학년 (${gradeData.year}년) - 학습활동 데이터 비교
        </div>
        <div class="chart-block-content">
            <div class="bar-charts-container">
                <div class="individual-bar-chart">
                    <div class="chart-title">자료구입비</div>
                    <canvas id="gradeCPSChart${grade}"></canvas>
                </div>
                <div class="individual-bar-chart">
                    <div class="chart-title">대출책수</div>
                    <canvas id="gradeLPSChart${grade}"></canvas>
                </div>
                <div class="individual-bar-chart">
                    <div class="chart-title">도서관방문수</div>
                    <canvas id="gradeVPSChart${grade}"></canvas>
                </div>
            </div>
            <div class="donut-charts-container">
                <div class="donut-chart-item">
                    <div class="chart-title">자료구입비 비율</div>
                    <canvas id="donutCPS${grade}" class="donut-chart"></canvas>
                    <div class="donut-label" id="labelCPS${grade}">-</div>
                </div>
                <div class="donut-chart-item">
                    <div class="chart-title">대출책수 비율</div>
                    <canvas id="donutLPS${grade}" class="donut-chart"></canvas>
                    <div class="donut-label" id="labelLPS${grade}">-</div>
                </div>
                <div class="donut-chart-item">
                    <div class="chart-title">도서관방문수 비율</div>
                    <canvas id="donutVPS${grade}" class="donut-chart"></canvas>
                    <div class="donut-label" id="labelVPS${grade}">-</div>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(blockDiv);
    
    // 개별 막대 차트들 생성
    await createIndividualBarCharts(grade, gradeData);
    
    // 도넛 차트들 생성
    await createGradeDonutCharts(grade, gradeData);
}

// 개별 막대 차트들 생성 (각각 적절한 스케일링 적용)
async function createIndividualBarCharts(grade, gradeData) {
    const dataTypes = [
        { key: 'CPS', label: '자료구입비', canvasId: `gradeCPSChart${grade}` },
        { key: 'LPS', label: '대출책수', canvasId: `gradeLPSChart${grade}` },
        { key: 'VPS', label: '도서관방문수', canvasId: `gradeVPSChart${grade}` }
    ];
    
    for (const dataType of dataTypes) {
        const ctx = document.getElementById(dataType.canvasId);
        if (!ctx) {
            console.error(`Canvas ${dataType.canvasId}를 찾을 수 없습니다.`);
            continue;
        }
        
        const userValue = gradeData.userData[dataType.key] || 0;
        const univValue = gradeData.universityData[dataType.key] || 0;
        
        console.log(`${dataType.label} - 유저: ${userValue}, 대학: ${univValue}`);
        
        // 스케일링을 위한 최소/최대값 계산
        const maxValue = Math.max(userValue, univValue);
        const minValue = Math.min(userValue, univValue);
        const range = maxValue - minValue;
        
        // 적절한 Y축 범위 설정
        let yMin, yMax;
        if (maxValue === 0) {
            yMin = 0;
            yMax = 10;
        } else if (range === 0) {
            yMin = Math.max(0, maxValue * 0.7);
            yMax = maxValue * 1.3;
        } else if (minValue === 0) {
            yMin = 0;
            yMax = maxValue * 1.2;
        } else {
            const padding = range * 0.3;
            yMin = Math.max(0, minValue - padding);
            yMax = maxValue + padding;
        }
        
        console.log(`${dataType.label} Y축 범위: ${yMin} ~ ${yMax}`);
        
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [''],  // 빈 라벨로 설정
                datasets: [
                    {
                        label: '유저',
                        data: [userValue],
                        backgroundColor: USER_COLOR + '80',
                        borderColor: USER_COLOR,
                        borderWidth: 1,
                        maxBarThickness: 40,
                        categoryPercentage: 0.8,
                        barPercentage: 0.9
                    },
                    {
                        label: '대학평균',
                        data: [univValue],
                        backgroundColor: UNIVERSITY_COLOR + '80',
                        borderColor: UNIVERSITY_COLOR,
                        borderWidth: 1,
                        maxBarThickness: 40,
                        categoryPercentage: 0.8,
                        barPercentage: 0.9
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 8 },
                            boxWidth: 8,
                            padding: 8
                        }
                    }
                },
                scales: {
                    y: {
                        min: yMin,
                        max: yMax,
                        ticks: {
                            font: { size: 7 },
                            maxTicksLimit: 5,
                            callback: function(value) {
                                if (value >= 1000) {
                                    return Math.round(value / 1000) + 'K';
                                }
                                return Math.round(value);
                            }
                        }
                    },
                    x: {
                        display: false  // X축 숨김
                    }
                },
                layout: {
                    padding: {
                        left: 5,
                        right: 5,
                        top: 5,
                        bottom: 5
                    }
                }
            }
        });
        
        analysisCharts.push(chart);
    }
}

// 학년별 도넛 차트들 생성
async function createGradeDonutCharts(grade, gradeData) {
    const dataTypes = ['CPS', 'LPS', 'VPS'];
    
    for (const dataType of dataTypes) {
        const ctx = document.getElementById(`donut${dataType}${grade}`);
        const labelElement = document.getElementById(`label${dataType}${grade}`);
        
        if (!ctx || !labelElement) continue;
        
        const userValue = gradeData.userData[dataType] || 0;
        const univValue = gradeData.universityData[dataType] || 0;
        
        const maxValue = Math.max(userValue, univValue);
        const minValue = Math.min(userValue, univValue);
        
        let percentage = 0;
        if (maxValue > 0) {
            percentage = Math.round((minValue / maxValue) * 100);
        }
        
        const isUserHigher = userValue >= univValue;
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [
                        isUserHigher ? USER_COLOR : UNIVERSITY_COLOR,
                        '#e0e0e0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '60%',
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // 라벨 업데이트
        const higherLabel = isUserHigher ? '유저' : '대학';
        const lowerLabel = isUserHigher ? '대학' : '유저';
        labelElement.innerHTML = `${lowerLabel}<br>${percentage}%`;
        
        analysisCharts.push(chart);
    }
}

// 환경점수 비교 블록 생성
async function createScoreComparisonBlock(container, grade, gradeData) {
    const blockDiv = document.createElement('div');
    blockDiv.className = 'chart-block';
    
    blockDiv.innerHTML = `
        <div class="chart-block-header">
            ${grade}학년 (${gradeData.year}년) - 환경점수 비교 분석
        </div>
        <div class="chart-block-content">
            <div class="score-comparison-block">
                <div class="user-score-chart">
                    <div class="chart-title">유저 vs 소속대학</div>
                    <canvas id="userScoreChart${grade}"></canvas>
                </div>
                <div class="similar-scores-chart">
                    <div class="chart-title">유사 점수 대학 비교</div>
                    <canvas id="similarScoresChart${grade}"></canvas>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(blockDiv);
    
    // 유저 vs 소속대학 차트
    await createUserUniversityScoreChart(grade, gradeData);
    
    // 유사 점수 대학 비교 차트
    await createSimilarScoresChart(grade, gradeData);
}

// 유저 vs 소속대학 환경점수 차트 (스케일링 개선)
async function createUserUniversityScoreChart(grade, gradeData) {
    const ctx = document.getElementById(`userScoreChart${grade}`);
    if (!ctx) return;
    
    const userScore = gradeData.userScore || 0;
    const univScore = gradeData.universityScore || 0;
    
    // 스케일링을 위한 범위 계산
    const maxValue = Math.max(userScore, univScore);
    const minValue = Math.min(userScore, univScore);
    const range = maxValue - minValue;
    
    let yMin, yMax;
    if (range === 0) {
        // 값이 같을 때
        yMin = Math.max(0, maxValue * 0.9);
        yMax = maxValue * 1.1;
    } else {
        // 차이를 더 명확하게 보이도록 패딩 추가
        const padding = Math.max(range * 0.3, 1);
        yMin = Math.max(0, minValue - padding);
        yMax = maxValue + padding;
    }
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['환경점수'],
            datasets: [
                {
                    label: '유저',
                    data: [userScore],
                    backgroundColor: USER_COLOR + '80',
                    borderColor: USER_COLOR,
                    borderWidth: 2,
                    maxBarThickness: 100
                },
                {
                    label: '소속대학',
                    data: [univScore],
                    backgroundColor: UNIVERSITY_COLOR + '80',
                    borderColor: UNIVERSITY_COLOR,
                    borderWidth: 2,
                    maxBarThickness: 100
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    min: yMin,
                    max: yMax,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        },
                        font: { size: 10 }
                    }
                }
            },
            layout: {
                padding: {
                    left: 5,
                    right: 5,
                    top: 5,
                    bottom: 5
                }
            }
        }
    });
    
    analysisCharts.push(chart);
}

// 유사 점수 대학 비교 차트 (정확한 5개 배치: -2, -1, 유저, +1, +2)
async function createSimilarScoresChart(grade, gradeData) {
    const ctx = document.getElementById(`similarScoresChart${grade}`);
    if (!ctx || !gradeData.similarUniversities) return;
    
    const userScore = gradeData.userScore || 0;
    const similarUnivs = gradeData.similarUniversities;
    
    console.log(`=== ${grade}학년 유사 점수 차트 생성 ===`);
    console.log('유저 점수:', userScore);
    console.log('유사 대학들:', similarUnivs);
    
    // 정확히 5개 배치: -2등, -1등, 유저, +1등, +2등 순서
    const chartData = [];
    
    // -2등 찾기 (가장 낮은 점수)
    const minus2 = similarUnivs.find(u => u.position === 'minus2');
    if (minus2) {
        chartData.push({
            name: minus2.name,
            score: minus2.score,
            isUser: false,
            label: minus2.name.length > 6 ? minus2.name.substring(0, 6) + '...' : minus2.name
        });
    }
    
    // -1등 찾기
    const minus1 = similarUnivs.find(u => u.position === 'minus1'); 
    if (minus1) {
        chartData.push({
            name: minus1.name,
            score: minus1.score,
            isUser: false,
            label: minus1.name.length > 6 ? minus1.name.substring(0, 6) + '...' : minus1.name
        });
    }
    
    // 유저 (반드시 3번째 위치)
    chartData.push({
        name: '유저',
        score: userScore,
        isUser: true,
        label: '유저'
    });
    
    // +1등 찾기
    const plus1 = similarUnivs.find(u => u.position === 'plus1');
    if (plus1) {
        chartData.push({
            name: plus1.name,
            score: plus1.score,
            isUser: false,
            label: plus1.name.length > 6 ? plus1.name.substring(0, 6) + '...' : plus1.name
        });
    }
    
    // +2등 찾기 (가장 높은 점수)
    const plus2 = similarUnivs.find(u => u.position === 'plus2');
    if (plus2) {
        chartData.push({
            name: plus2.name,
            score: plus2.score,
            isUser: false,
            label: plus2.name.length > 6 ? plus2.name.substring(0, 6) + '...' : plus2.name
        });
    }
    
    console.log('최종 차트 데이터 (순서대로):', chartData.map((item, index) => ({
        position: index + 1,
        name: item.name,
        score: item.score,
        isUser: item.isUser
    })));
    
    // 정확히 5개인지 확인
    if (chartData.length !== 5) {
        console.warn(`차트 데이터가 5개가 아닙니다: ${chartData.length}개`);
        
        // 부족한 경우 빈 데이터로 채우기
        while (chartData.length < 5) {
            const position = chartData.length;
            if (position < 2) {
                // 앞쪽에 빈 데이터
                chartData.unshift({
                    name: `데이터없음${position + 1}`,
                    score: 0,
                    isUser: false,
                    label: '-'
                });
            } else {
                // 뒤쪽에 빈 데이터  
                chartData.push({
                    name: `데이터없음${position + 1}`,
                    score: 0,
                    isUser: false,
                    label: '-'
                });
            }
        }
    }
    
    const scores = chartData.map(item => item.score);
    const maxScore = Math.max(...scores);
    const minScore = Math.min(...scores.filter(s => s > 0)); // 0 제외
    const range = maxScore - minScore;
    
    // 스케일링 범위 설정
    let yMin, yMax;
    if (range === 0 || minScore === undefined) {
        yMin = Math.max(0, maxScore * 0.95);
        yMax = maxScore * 1.05;
    } else {
        const padding = Math.max(range * 0.15, 0.5);
        yMin = Math.max(0, minScore - padding);
        yMax = maxScore + padding;
    }
    
    const labels = chartData.map(item => item.label);
    const colors = chartData.map(item => item.isUser ? USER_COLOR : '#81c784');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '환경점수',
                data: scores,
                backgroundColor: colors.map(color => color + '80'),
                borderColor: colors,
                borderWidth: 2,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    min: yMin,
                    max: yMax,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        },
                        font: { size: 10 }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 9 }
                    }
                }
            },
            layout: {
                padding: {
                    left: 5,
                    right: 5,
                    top: 5,
                    bottom: 5
                }
            }
        }
    });
    
    analysisCharts.push(chart);
}

// 네비게이션 함수
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

// 결과 저장
function exportAnalysis() {
    if (!currentUserData) {
        alert('분석할 유저를 먼저 선택해주세요.');
        return;
    }
    
    if (analysisCharts.length === 0) {
        alert('분석 결과가 없습니다. 먼저 분석을 실행해주세요.');
        return;
    }
    
    try {
        // 간단한 텍스트 결과 저장
        const analysisResult = {
            user: currentUserData.USR_NAME,
            university: currentUserData.USR_SNM,
            timestamp: new Date().toISOString(),
            grades: {}
        };
        
        for (let grade = 1; grade <= 4; grade++) {
            const year = currentUserData[`${grade === 1 ? '1ST' : grade === 2 ? '2ND' : grade === 3 ? '3RD' : '4TH'}_YR`];
            if (year) {
                analysisResult.grades[grade] = {
                    year: year,
                    userScore: currentUserData[`SCR_EST_${grade === 1 ? '1ST' : grade === 2 ? '2ND' : grade === 3 ? '3RD' : '4TH'}`]
                };
            }
        }
        
        const jsonString = JSON.stringify(analysisResult, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `libra_user_analysis_${currentUserData.USR_NAME}_${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('분석 결과 저장 완료');
    } catch (error) {
        console.error('분석 결과 저장 실패:', error);
        alert('분석 결과 저장에 실패했습니다.');
    }
}

// 로딩 표시
function showLoading() {
    const chartGrid = document.getElementById('chartGrid');
    chartGrid.innerHTML = `
        <div class="loading-message">
            <div class="loading-spinner"></div>
            <p>분석 중입니다. 잠시만 기다려주세요...</p>
        </div>
    `;
}

// 로딩 숨김
function hideLoading() {
    // createAllCharts에서 처리됨
}

// 에러 표시
function showError(message) {
    const chartGrid = document.getElementById('chartGrid');
    const placeholder = document.getElementById('chartPlaceholder');
    
    if (placeholder) {
        placeholder.innerHTML = `
            <div class="placeholder-content">
                <div class="placeholder-icon">⚠️</div>
                <h3>오류 발생</h3>
                <p>${message}</p>
                <div class="error-message" style="display: block;">
                    CSV 파일 경로를 확인해주세요:<br>
                    - ../../resource/csv_files/유저환경점수.csv<br>
                    - ../../resource/csv_files/csv_data/Num06_종합데이터_YYYY.csv<br>
                    - ../../resource/csv_files/예측데이터총합.csv
                </div>
            </div>
        `;
        placeholder.style.display = 'flex';
    }
}

// 페이지 초기화
function initializePage() {
    console.log('유저 분석 페이지 초기화');
    
    // 유저 데이터 로드
    loadUserData();
}

// 디버깅용 함수들
function debugInfo() {
    console.log('=== 유저 분석 디버깅 정보 ===');
    console.log('유저 데이터:', userDataCSV ? userDataCSV.length + '명' : '없음');
    console.log('예측 데이터:', predictionDataCSV ? predictionDataCSV.length + '행' : '없음');
    console.log('연도별 데이터 캐시:', Object.keys(yearlyDataCache));
    console.log('현재 선택된 유저:', currentUserData);
    console.log('활성 차트 수:', analysisCharts.length);
    
    if (currentUserData) {
        console.log('선택된 유저 정보:', {
            name: currentUserData.USR_NAME,
            university: currentUserData.USR_SNM,
            grades: {
                '1st': { year: currentUserData['1ST_YR'], score: currentUserData['SCR_EST_1ST'] },
                '2nd': { year: currentUserData['2ND_YR'], score: currentUserData['SCR_EST_2ND'] },
                '3rd': { year: currentUserData['3RD_YR'], score: currentUserData['SCR_EST_3RD'] },
                '4th': { year: currentUserData['4TH_YR'], score: currentUserData['SCR_EST_4TH'] }
            }
        });
    }
}

// 전역 함수 등록
window.libra_user = {
    userDataCSV,
    predictionDataCSV,
    yearlyDataCache,
    currentUserData,
    analysisCharts,
    debugInfo,
    loadUserData,
    loadYearlyData,
    loadPredictionData,
    generateUserAnalysis,
    // 테스트 함수들
    testUserData: function() {
        if (userDataCSV) {
            console.log('유저 데이터 구조:', Object.keys(userDataCSV[0] || {}));
            console.log('첫 번째 유저:', userDataCSV[0]);
        }
    },
    testYearlyData: function(year) {
        if (yearlyDataCache[year]) {
            const data = yearlyDataCache[year];
            console.log(`${year}년 데이터:`, data.length, '행');
            console.log('컬럼:', Object.keys(data[0] || {}));
        } else {
            console.log(`${year}년 데이터가 캐시에 없습니다.`);
        }
    },
    testPredictionData: function() {
        if (predictionDataCSV) {
            console.log('예측 데이터 구조:', Object.keys(predictionDataCSV[0] || {}));
            console.log('첫 번째 행:', predictionDataCSV[0]);
            
            // 점수 컬럼 확인
            const scoreColumns = Object.keys(predictionDataCSV[0]).filter(key => key.startsWith('SCR_EST_'));
            console.log('점수 컬럼들:', scoreColumns);
        }
    },
    findUniversity: function(universityName, year) {
        if (yearlyDataCache[year]) {
            const found = yearlyDataCache[year].find(row => row.SNM === universityName);
            console.log(`${year}년 ${universityName} 데이터:`, found);
            return found;
        }
        console.log(`${year}년 데이터가 없습니다.`);
        return null;
    }
};

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        generateUserAnalysis();
    }
    
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        exportAnalysis();
    }
});

// 페이지 로드 완료 시 초기화
window.addEventListener('load', function() {
    initializePage();
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('유저 분석 페이지 DOM 로드 완료');
    
    if (document.readyState === 'complete') {
        initializePage();
    }
});

// 페이지 떠날 때 차트 정리
window.addEventListener('beforeunload', function() {
    analysisCharts.forEach(chart => {
        if (chart) chart.destroy();
    });
    console.log('유저 분석 페이지를 떠납니다.');
});