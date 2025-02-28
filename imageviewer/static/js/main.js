document.addEventListener('DOMContentLoaded', function() {
    // モーダル関連の処理
    const imageModals = document.querySelectorAll('.modal');
    imageModals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function(event) {
            // モーダルが表示される直前の処理
            const button = event.relatedTarget;
            const card = button.closest('.card');
            const image = card.querySelector('img');

            // モーダル内の画像を最適化
            const modalImage = this.querySelector('.modal-body img');
            modalImage.style.maxHeight = window.innerHeight * 0.7 + 'px';
        });
    });

    // 画像の遅延読み込み
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const lazyLoadScript = document.createElement('script');
        lazyLoadScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/lozad.js/1.16.0/lozad.min.js';
        document.body.appendChild(lazyLoadScript);

        lazyLoadScript.onload = function() {
            const observer = lozad('.lazy');
            observer.observe();
        }
    }

    // ページネーションのURL処理
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.classList.contains('disabled')) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// 画像モーダルのキーボードナビゲーション
document.addEventListener('keydown', function(e) {
    const activeModal = document.querySelector('.modal.show');
    if (!activeModal) return;

    if (e.key === 'Escape') {
        const modal = bootstrap.Modal.getInstance(activeModal);
        modal.hide();
    }
});