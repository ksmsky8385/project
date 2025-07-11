// 페이지 네비게이션 함수
function navigateTo(page) {
    console.log(`${page} 페이지로 이동`);
    
    // 실제 페이지 이동 로직을 여기에 구현
    switch(page) {
        case 'learning':
            // alert('학습환경 분석 페이지로 이동합니다.'); // 이 줄 삭제 또는 주석처리
            window.location.href = '../html/page_chartpage_num01.html'; // 이 줄 추가
            break;
        case 'development':
            alert('발전도 분석 페이지로 이동합니다.');
            // window.location.href = 'development-analysis.html';
            break;
        case 'site-guide':
            alert('사이트 이용 방법 페이지로 이동합니다.');
            // window.location.href = 'site-guide.html';
            break;
        case 'usage-stats':
            alert('이용 수치 가이드 페이지로 이동합니다.');
            // window.location.href = 'usage-stats.html';
            break;
        case 'site-info':
            alert('사이트 정보 페이지로 이동합니다.');
            // window.location.href = 'site-info.html';
            break;
        default:
            alert('페이지를 찾을 수 없습니다.');
    }
}
// 로그인 함수
function showLogin() {
    alert('로그인 페이지로 이동합니다.');
    
    // 실제 로그인 모달이나 페이지 로직을 여기에 구현
    // 예: 모달 창 열기, 로그인 페이지로 이동 등
    // window.location.href = 'login.html';
    
    // 또는 모달 창 구현 예시:
    // showLoginModal();
}

// 공지사항 상세 보기 함수
function showAnnouncement(title) {
    alert(`공지사항: ${title}`);
    
    // 실제 공지사항 상세 페이지 로직을 여기에 구현
    // window.location.href = `announcement-detail.html?title=${encodeURIComponent(title)}`;
}

// 반응형 메뉴 토글 함수 (모바일용)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('mobile-open');
}

// 스크롤 이벤트 처리 (헤더 그림자 효과)
function handleScroll() {
    const header = document.querySelector('header');
    if (window.scrollY > 10) {
        header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.15)';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    }
}

// 페이지 로드 시 초기화
function initializePage() {
    // 페이지 로드 애니메이션
    document.body.style.opacity = '1';
    
    // 이벤트 리스너 등록
    window.addEventListener('scroll', handleScroll);
    
    // 카드 hover 효과 향상
    const heroCards = document.querySelectorAll('.hero-card');
    heroCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // 공지사항 아이템 hover 효과
    const announcementItems = document.querySelectorAll('.announcement-item');
    announcementItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.paddingLeft = '15px';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.paddingLeft = '0';
        });
    });
}

// 모달 관련 함수들 (추후 구현용)
function showLoginModal() {
    // 로그인 모달 창 구현
    console.log('로그인 모달을 표시합니다.');
}

function closeLoginModal() {
    // 로그인 모달 창 닫기
    console.log('로그인 모달을 닫습니다.');
}

// 유틸리티 함수들
function showLoading() {
    // 로딩 스피너 표시
    console.log('로딩 중...');
}

function hideLoading() {
    // 로딩 스피너 숨기기
    console.log('로딩 완료');
}

// 에러 처리 함수
function handleError(error) {
    console.error('에러 발생:', error);
    alert('오류가 발생했습니다. 다시 시도해주세요.');
}

// 페이지 로드 완료 시 초기화 실행
window.addEventListener('load', initializePage);

// DOM 콘텐츠 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 로드 완료');
    
    // 추가 초기화 코드가 있다면 여기에 작성
});

// 페이지 언로드 시 정리 작업
window.addEventListener('beforeunload', function() {
    // 필요한 정리 작업 수행
    console.log('페이지를 떠납니다.');
});