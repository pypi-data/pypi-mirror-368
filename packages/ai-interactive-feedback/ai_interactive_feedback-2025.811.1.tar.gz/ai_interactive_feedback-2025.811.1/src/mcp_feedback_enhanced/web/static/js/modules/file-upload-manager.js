/**
 * 現代化檔案上傳管理器
 * 使用事件委託模式，避免重複事件監聽器問題
 */

(function() {
    'use strict';

    // 確保命名空間存在
    if (!window.MCPFeedback) {
        window.MCPFeedback = {};
    }

    /**
     * 檔案上傳管理器建構函數
     */
    function FileUploadManager(options) {
        options = options || {};

        // 配置選項
        this.maxFileSize = options.maxFileSize || 0; // 0 表示無限制
        this.enableBase64Detail = options.enableBase64Detail || false;
        this.acceptedTypes = options.acceptedTypes || 'image/*';
        this.maxFiles = options.maxFiles || 10;

        // 狀態管理
        this.files = [];
        this.isInitialized = false;
        this.debounceTimeout = null;
        this.lastClickTime = 0;
        this.isProcessingClick = false;
        this.lastClickTime = 0;
        this.lightboxOverlay = null; // 圖片放大預覽遮罩
        this.lightboxImage = null;   // 放大顯示的圖片元素
        this.lightboxClose = null;   // 關閉按鈕元素
        this.lightboxPrevBtn = null; // 上一張按鈕
        this.lightboxNextBtn = null; // 下一張按鈕
        this.lightboxCounter = null; // 圖片計數器
        this.currentImageIndex = 0;  // 當前圖片索引

        // 事件回調
        this.onFileAdd = options.onFileAdd || null;
        this.onFileRemove = options.onFileRemove || null;
        this.onSettingsChange = options.onSettingsChange || null;

        // 綁定方法上下文
        this.handleDelegatedEvent = this.handleDelegatedEvent.bind(this);
        this.handleGlobalPaste = this.handleGlobalPaste.bind(this);

        console.log('📁 FileUploadManager 初始化完成');
    }

    /**
     * 初始化檔案上傳管理器
     */
    FileUploadManager.prototype.initialize = function() {
        if (this.isInitialized) {
            console.warn('⚠️ FileUploadManager 已經初始化過了');
            return;
        }

        this.setupEventDelegation();
        this.setupGlobalPasteHandler();
        // 初始化圖片放大預覽（Lightbox）
        this.setupLightbox();
        this.isInitialized = true;

        console.log('✅ FileUploadManager 事件委託設置完成');
    };

    /**
     * 設置事件委託
     * 使用單一事件監聽器處理所有檔案上傳相關事件
     */
    FileUploadManager.prototype.setupEventDelegation = function() {
        // 移除舊的事件監聽器
        document.removeEventListener('click', this.handleDelegatedEvent);
        document.removeEventListener('dragover', this.handleDelegatedEvent);
        document.removeEventListener('dragleave', this.handleDelegatedEvent);
        document.removeEventListener('drop', this.handleDelegatedEvent);
        document.removeEventListener('change', this.handleDelegatedEvent);

        // 設置新的事件委託
        document.addEventListener('click', this.handleDelegatedEvent);

        /**
         * 初始化 Lightbox 預覽
         */
        FileUploadManager.prototype.setupLightbox = function() {
            if (this.lightboxOverlay) return;

            const overlay = document.createElement('div');
            overlay.className = 'image-lightbox-overlay';
            overlay.style.cssText = [
                'position: fixed',
                'inset: 0',
                'background: rgba(0,0,0,0.8)',
                'display: none',
                'align-items: center',
                'justify-content: center',
                'z-index: 9999',
                'padding: 20px',
            ].join(';');

            // 圖片容器，用於更好的居中控制
            const imageContainer = document.createElement('div');
            imageContainer.className = 'image-lightbox-container';
            imageContainer.style.cssText = [
                'position: relative',
                'display: flex',
                'flex-direction: column',
                'align-items: center',
                'justify-content: center',
                'max-width: 90vw',
                'max-height: 90vh'
            ].join(';');

            const img = document.createElement('img');
            img.className = 'image-lightbox-img';
            img.style.cssText = [
                'max-width: 100%',
                'max-height: calc(90vh - 80px)', // 為底部控件留出空間
                'object-fit: contain',
                'border-radius: 8px',
                'box-shadow: 0 10px 30px rgba(0,0,0,0.5)',
                'display: block'
            ].join(';');

            // 底部導航控件容器
            const navContainer = document.createElement('div');
            navContainer.className = 'image-lightbox-nav';
            navContainer.style.cssText = [
                'display: flex',
                'align-items: center',
                'justify-content: center',
                'gap: 20px',
                'margin-top: 20px',
                'padding: 10px 20px',
                'background: rgba(0,0,0,0.5)',
                'border-radius: 25px',
                'backdrop-filter: blur(10px)'
            ].join(';');

            // 上一張按鈕
            const prevBtn = document.createElement('button');
            prevBtn.className = 'image-lightbox-prev';
            prevBtn.textContent = '‹';
            prevBtn.setAttribute('aria-label', '上一張圖片');
            prevBtn.style.cssText = [
                'width: 40px',
                'height: 40px',
                'border-radius: 50%',
                'background: rgba(255,255,255,0.9)',
                'color: #333',
                'border: none',
                'cursor: pointer',
                'font-size: 20px',
                'font-weight: bold',
                'display: flex',
                'align-items: center',
                'justify-content: center',
                'transition: all 0.3s ease',
                'box-shadow: 0 2px 8px rgba(0,0,0,0.3)'
            ].join(';');

            // 圖片計數器
            const counter = document.createElement('span');
            counter.className = 'image-lightbox-counter';
            counter.style.cssText = [
                'color: #fff',
                'font-size: 14px',
                'font-weight: 500',
                'min-width: 60px',
                'text-align: center',
                'text-shadow: 0 1px 2px rgba(0,0,0,0.5)'
            ].join(';');

            // 下一張按鈕
            const nextBtn = document.createElement('button');
            nextBtn.className = 'image-lightbox-next';
            nextBtn.textContent = '›';
            nextBtn.setAttribute('aria-label', '下一張圖片');
            nextBtn.style.cssText = [
                'width: 40px',
                'height: 40px',
                'border-radius: 50%',
                'background: rgba(255,255,255,0.9)',
                'color: #333',
                'border: none',
                'cursor: pointer',
                'font-size: 20px',
                'font-weight: bold',
                'display: flex',
                'align-items: center',
                'justify-content: center',
                'transition: all 0.3s ease',
                'box-shadow: 0 2px 8px rgba(0,0,0,0.3)'
            ].join(';');

            // 關閉按鈕
            const closeBtn = document.createElement('button');
            closeBtn.className = 'image-lightbox-close';
            closeBtn.textContent = '×';
            closeBtn.setAttribute('aria-label', '關閉預覽');
            closeBtn.style.cssText = [
                'position: absolute',
                'top: 16px',
                'right: 16px',
                'width: 40px',
                'height: 40px',
                'border-radius: 50%',
                'background: rgba(255,255,255,0.9)',
                'color: #333',
                'border: none',
                'cursor: pointer',
                'font-size: 24px',
                'font-weight: bold',
                'display: flex',
                'align-items: center',
                'justify-content: center',
                'transition: all 0.3s ease',
                'box-shadow: 0 2px 8px rgba(0,0,0,0.3)'
            ].join(';');

            // 組裝元素
            navContainer.appendChild(prevBtn);
            navContainer.appendChild(counter);
            navContainer.appendChild(nextBtn);

            imageContainer.appendChild(img);
            imageContainer.appendChild(navContainer);

            overlay.appendChild(imageContainer);
            overlay.appendChild(closeBtn);
            document.body.appendChild(overlay);

            // 按鈕懸停效果
            [prevBtn, nextBtn, closeBtn].forEach(btn => {
                btn.addEventListener('mouseenter', () => {
                    btn.style.background = 'rgba(255,255,255,1)';
                    btn.style.transform = 'scale(1.1)';
                });
                btn.addEventListener('mouseleave', () => {
                    btn.style.background = 'rgba(255,255,255,0.9)';
                    btn.style.transform = 'scale(1)';
                });
            });

            // 事件處理
            const self = this;
            const hide = () => {
                overlay.style.display = 'none';
                img.src = '';
                self.currentImageIndex = 0;
            };

            // 關閉事件
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay || e.target === closeBtn) hide();
            });
            closeBtn.addEventListener('click', hide);

            // 導航事件
            prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                self.showPreviousImage();
            });
            nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                self.showNextImage();
            });

            // 鍵盤事件
            document.addEventListener('keydown', (e) => {
                if (overlay.style.display === 'block') {
                    switch(e.key) {
                        case 'Escape':
                            hide();
                            break;
                        case 'ArrowLeft':
                            e.preventDefault();
                            self.showPreviousImage();
                            break;
                        case 'ArrowRight':
                            e.preventDefault();
                            self.showNextImage();
                            break;
                    }
                }
            });

            this.lightboxOverlay = overlay;
            this.lightboxImage = img;
            this.lightboxClose = closeBtn;
            this.lightboxPrevBtn = prevBtn;
            this.lightboxNextBtn = nextBtn;
            this.lightboxCounter = counter;
        };

        /**
         * 顯示 Lightbox
         */
        FileUploadManager.prototype.showLightbox = function(src, index) {
            if (!this.lightboxOverlay) this.setupLightbox();

            // 如果提供了索引，使用索引；否則根據 src 查找索引
            if (typeof index === 'number') {
                this.currentImageIndex = index;
            } else {
                // 根據 src 查找對應的圖片索引
                this.currentImageIndex = this.files.findIndex(file => {
                    const fileSrc = 'data:' + file.type + ';base64,' + file.data;
                    return fileSrc === src;
                });
                if (this.currentImageIndex === -1) this.currentImageIndex = 0;
            }

            this.updateLightboxImage();
            this.lightboxOverlay.style.display = 'block';
        };

        /**
         * 更新 Lightbox 圖片顯示
         */
        FileUploadManager.prototype.updateLightboxImage = function() {
            if (!this.lightboxOverlay || this.files.length === 0) return;

            const currentFile = this.files[this.currentImageIndex];
            if (!currentFile) return;

            const src = 'data:' + currentFile.type + ';base64,' + currentFile.data;
            this.lightboxImage.src = src;
            this.lightboxImage.alt = currentFile.name;

            // 更新計數器
            this.lightboxCounter.textContent = `${this.currentImageIndex + 1}/${this.files.length}`;

            // 更新按鈕狀態
            this.lightboxPrevBtn.style.opacity = this.currentImageIndex > 0 ? '1' : '0.5';
            this.lightboxPrevBtn.style.cursor = this.currentImageIndex > 0 ? 'pointer' : 'not-allowed';
            this.lightboxPrevBtn.disabled = this.currentImageIndex === 0;

            this.lightboxNextBtn.style.opacity = this.currentImageIndex < this.files.length - 1 ? '1' : '0.5';
            this.lightboxNextBtn.style.cursor = this.currentImageIndex < this.files.length - 1 ? 'pointer' : 'not-allowed';
            this.lightboxNextBtn.disabled = this.currentImageIndex === this.files.length - 1;

            // 如果只有一張圖片，隱藏導航控件
            const navContainer = this.lightboxOverlay.querySelector('.image-lightbox-nav');
            if (navContainer) {
                navContainer.style.display = this.files.length > 1 ? 'flex' : 'none';
            }
        };

        /**
         * 顯示上一張圖片
         */
        FileUploadManager.prototype.showPreviousImage = function() {
            if (this.currentImageIndex > 0) {
                this.currentImageIndex--;
                this.updateLightboxImage();
            }
        };

        /**
         * 顯示下一張圖片
         */
        FileUploadManager.prototype.showNextImage = function() {
            if (this.currentImageIndex < this.files.length - 1) {
                this.currentImageIndex++;
                this.updateLightboxImage();
            }
        };

        document.addEventListener('dragover', this.handleDelegatedEvent);
        document.addEventListener('dragleave', this.handleDelegatedEvent);
        document.addEventListener('drop', this.handleDelegatedEvent);
        document.addEventListener('change', this.handleDelegatedEvent);
    };

    /**
     * 處理委託事件
     */
    FileUploadManager.prototype.handleDelegatedEvent = function(event) {
        const target = event.target;

        // 處理檔案移除按鈕點擊
        const removeBtn = target.closest('.image-remove-btn');
        if (removeBtn) {
            event.preventDefault();
            event.stopPropagation();
            this.handleRemoveFile(removeBtn);
            return;
        }

        // 處理檔案輸入變更
        if (target.type === 'file' && event.type === 'change') {
            this.handleFileInputChange(target, event);
            return;
        }

        // 處理上傳區域事件 - 只處理直接點擊上傳區域的情況
        const uploadArea = target.closest('.image-upload-area');
        if (uploadArea && event.type === 'click') {
            // 確保不是點擊 input 元素本身
            if (target.type === 'file') {
                return;
            }

            // 確保不是點擊預覽圖片或移除按鈕
            if (target.closest('.image-preview-item') || target.closest('.image-remove-btn')) {
                return;
            }

            this.handleUploadAreaClick(uploadArea, event);
            return;
        }

        // 處理拖放事件
        if (uploadArea && (event.type === 'dragover' || event.type === 'dragleave' || event.type === 'drop')) {
            switch (event.type) {
                case 'dragover':
                    this.handleDragOver(uploadArea, event);
                    break;
                case 'dragleave':
                    this.handleDragLeave(uploadArea, event);
                    break;
                case 'drop':
                    this.handleDrop(uploadArea, event);
                    break;
            }
        }
    };

    /**
     * 處理上傳區域點擊（使用防抖機制）
     */
    FileUploadManager.prototype.handleUploadAreaClick = function(uploadArea, event) {
        event.preventDefault();
        event.stopPropagation();

        // 強力防抖機制 - 防止無限循環
        const now = Date.now();
        if (this.lastClickTime && (now - this.lastClickTime) < 500) {
            console.log('🚫 防抖：忽略重複點擊，間隔:', now - this.lastClickTime, 'ms');
            return;
        }
        this.lastClickTime = now;

        // 如果已經有待處理的點擊，忽略新的點擊
        if (this.isProcessingClick) {
            console.log('🚫 正在處理點擊，忽略新的點擊');
            return;
        }

        this.isProcessingClick = true;

        const fileInput = uploadArea.querySelector('input[type="file"]');
        if (fileInput) {
            console.log('🖱️ 觸發檔案選擇:', fileInput.id);

            // 重置 input 值以確保可以重複選擇同一檔案
            fileInput.value = '';

            // 使用 setTimeout 確保在下一個事件循環中執行，避免事件冒泡問題
            const self = this;
            setTimeout(function() {
                try {
                    fileInput.click();
                    console.log('✅ 檔案選擇對話框已觸發');
                } catch (error) {
                    console.error('❌ 檔案選擇對話框觸發失敗:', error);
                } finally {
                    // 重置處理狀態
                    setTimeout(function() {
                        self.isProcessingClick = false;
                    }, 100);
                }
            }, 50);
        } else {
            this.isProcessingClick = false;
        }
    };

    /**
     * 處理檔案輸入變更
     */
    FileUploadManager.prototype.handleFileInputChange = function(fileInput, event) {
        const files = event.target.files;
        if (files && files.length > 0) {
            console.log('📁 檔案選擇變更:', files.length, '個檔案');
            this.processFiles(Array.from(files), fileInput);
        }
    };

    /**
     * 處理拖放事件
     */
    FileUploadManager.prototype.handleDragOver = function(uploadArea, event) {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    };

    FileUploadManager.prototype.handleDragLeave = function(uploadArea, event) {
        event.preventDefault();
        // 只有當滑鼠真正離開上傳區域時才移除樣式
        if (!uploadArea.contains(event.relatedTarget)) {
            uploadArea.classList.remove('dragover');
        }
    };

    FileUploadManager.prototype.handleDrop = function(uploadArea, event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = event.dataTransfer.files;
        if (files && files.length > 0) {
            console.log('📁 拖放檔案:', files.length, '個檔案');
            this.processFiles(Array.from(files), uploadArea.querySelector('input[type="file"]'));
        }
    };

    /**
     * 處理檔案移除
     */
    FileUploadManager.prototype.handleRemoveFile = function(removeBtn) {
        const index = parseInt(removeBtn.dataset.index);
        if (!isNaN(index) && index >= 0 && index < this.files.length) {
            const removedFile = this.files.splice(index, 1)[0];
            console.log('🗑️ 移除檔案:', removedFile.name);

            this.updateAllPreviews();

            if (this.onFileRemove) {
                this.onFileRemove(removedFile, index);
            }
        }
    };

    /**
     * 設置全域剪貼板貼上處理
     */
    FileUploadManager.prototype.setupGlobalPasteHandler = function() {
        document.removeEventListener('paste', this.handleGlobalPaste);
        document.addEventListener('paste', this.handleGlobalPaste);
    };

    /**
     * 處理全域剪貼板貼上
     */
    FileUploadManager.prototype.handleGlobalPaste = function(event) {
        const items = event.clipboardData.items;
        const imageFiles = [];

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                if (file) {
                    imageFiles.push(file);
                }
            }
        }

        if (imageFiles.length > 0) {
            event.preventDefault();
            console.log('📋 剪貼板貼上圖片:', imageFiles.length, '個檔案');
            this.processFiles(imageFiles);
        }
    };

    /**
     * 處理檔案
     */
    FileUploadManager.prototype.processFiles = function(files, sourceInput) {
        const validFiles = [];

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // 檢查檔案類型
            if (!file.type.startsWith('image/')) {
                console.warn('⚠️ 跳過非圖片檔案:', file.name);
                continue;
            }

            // 檢查檔案大小
            if (this.maxFileSize > 0 && file.size > this.maxFileSize) {
                const sizeLimit = this.formatFileSize(this.maxFileSize);
                console.warn('⚠️ 檔案過大:', file.name, '超過限制', sizeLimit);
                const message = window.i18nManager ?
                    window.i18nManager.t('fileUpload.fileSizeExceeded', {
                        limit: sizeLimit,
                        filename: file.name
                    }) :
                    '圖片大小超過限制 (' + sizeLimit + '): ' + file.name;
                this.showMessage(message, 'warning');
                continue;
            }

            // 檢查檔案數量限制
            if (this.files.length + validFiles.length >= this.maxFiles) {
                console.warn('⚠️ 檔案數量超過限制:', this.maxFiles);
                const message = window.i18nManager ?
                    window.i18nManager.t('fileUpload.maxFilesExceeded', { maxFiles: this.maxFiles }) :
                    '最多只能上傳 ' + this.maxFiles + ' 個檔案';
                this.showMessage(message, 'warning');
                break;
            }

            validFiles.push(file);
        }

        // 處理有效檔案
        if (validFiles.length > 0) {
            this.addFiles(validFiles);
        }
    };

    /**
     * 添加檔案到列表
     */
    FileUploadManager.prototype.addFiles = function(files) {
        const promises = files.map(file => this.fileToBase64(file));

        const self = this;
        Promise.all(promises)
            .then(function(base64Results) {
                base64Results.forEach(function(base64, index) {
                    const file = files[index];
                    const fileData = {
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        data: base64,
                        timestamp: Date.now()
                    };

                    self.files.push(fileData);
                    console.log('✅ 檔案已添加:', file.name);

                    if (self.onFileAdd) {
                        self.onFileAdd(fileData);
                    }
                });

                self.updateAllPreviews();
            })
            .catch(function(error) {
                console.error('❌ 檔案處理失敗:', error);
                const message = window.i18nManager ?
                    window.i18nManager.t('fileUpload.processingFailed', '檔案處理失敗，請重試') :
                    '檔案處理失敗，請重試';
                self.showMessage(message, 'error');
            });
    };

    /**
     * 將檔案轉換為 Base64
     */
    FileUploadManager.prototype.fileToBase64 = function(file) {
        return new Promise(function(resolve, reject) {
            const reader = new FileReader();
            reader.onload = function() {
                resolve(reader.result.split(',')[1]);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    };

    /**
     * 更新所有預覽容器
     */
    FileUploadManager.prototype.updateAllPreviews = function() {
        const previewContainers = document.querySelectorAll('.image-preview-container');
        const self = this;

        previewContainers.forEach(function(container) {
            self.updatePreviewContainer(container);
        });

        this.updateFileCount();
        console.log('🖼️ 已更新', previewContainers.length, '個預覽容器');
    };

    /**
     * 更新單個預覽容器
     */
    FileUploadManager.prototype.updatePreviewContainer = function(container) {
        container.innerHTML = '';

        const self = this;
        this.files.forEach(function(file, index) {
            const previewElement = self.createPreviewElement(file, index);
            container.appendChild(previewElement);
        });
    };

    /**
     * 創建預覽元素
     */
    FileUploadManager.prototype.createPreviewElement = function(file, index) {
        const preview = document.createElement('div');
        preview.className = 'image-preview-item';

        // 圖片元素
        const img = document.createElement('img');
        img.src = 'data:' + file.type + ';base64,' + file.data;
        img.alt = file.name;
        img.title = file.name + ' (' + this.formatFileSize(file.size) + ')';

        // 檔案資訊
        const info = document.createElement('div');
        info.className = 'image-info';

        const name = document.createElement('div');
        name.className = 'image-name';
        name.textContent = file.name;

        const size = document.createElement('div');
        size.className = 'image-size';
        size.textContent = this.formatFileSize(file.size);

        // 移除按鈕
        const removeBtn = document.createElement('button');
        removeBtn.className = 'image-remove-btn';
        removeBtn.textContent = '×';
        removeBtn.title = '移除圖片';
        removeBtn.dataset.index = index;
        removeBtn.setAttribute('aria-label', '移除圖片 ' + file.name);

        // 組裝元素
        info.appendChild(name);
        info.appendChild(size);
        // 點擊縮略圖顯示原圖（Lightbox）
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', () => {
            const src = img.src; // data URL
            this.showLightbox(src, index);
        });

        preview.appendChild(img);
        preview.appendChild(info);
        preview.appendChild(removeBtn);

        return preview;
    };

    /**
     * 更新檔案計數顯示
     */
    FileUploadManager.prototype.updateFileCount = function() {
        const count = this.files.length;
        const countElements = document.querySelectorAll('.image-count');

        countElements.forEach(function(element) {
            element.textContent = count > 0 ? '(' + count + ')' : '';
        });

        // 更新上傳區域狀態
        const uploadAreas = document.querySelectorAll('.image-upload-area');
        uploadAreas.forEach(function(area) {
            if (count > 0) {
                area.classList.add('has-images');
            } else {
                area.classList.remove('has-images');
            }
        });
    };

    /**
     * 格式化檔案大小
     */
    FileUploadManager.prototype.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    /**
     * 顯示訊息
     */
    FileUploadManager.prototype.showMessage = function(message, type) {
        // 使用現有的 Utils.showMessage 如果可用
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            const messageType = type === 'warning' ? window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING :
                               type === 'error' ? window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR :
                               window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO;
            window.MCPFeedback.Utils.showMessage(message, messageType);
        } else {
            // 後備方案
            console.log('[' + type.toUpperCase() + ']', message);
            alert(message);
        }
    };

    /**
     * 更新設定
     */
    FileUploadManager.prototype.updateSettings = function(settings) {
        this.maxFileSize = settings.imageSizeLimit || 0;
        this.enableBase64Detail = settings.enableBase64Detail || false;

        console.log('⚙️ FileUploadManager 設定已更新:', {
            maxFileSize: this.maxFileSize,
            enableBase64Detail: this.enableBase64Detail
        });
    };

    /**
     * 獲取檔案列表
     */
    FileUploadManager.prototype.getFiles = function() {
        return this.files.slice(); // 返回副本
    };

    /**
     * 清空所有檔案
     */
    FileUploadManager.prototype.clearFiles = function() {
        this.files = [];
        this.updateAllPreviews();
        console.log('🗑️ 已清空所有檔案');
    };

    /**
     * 清理資源
     */
    FileUploadManager.prototype.cleanup = function() {
        // 移除事件監聽器
        document.removeEventListener('click', this.handleDelegatedEvent);
        document.removeEventListener('dragover', this.handleDelegatedEvent);
        document.removeEventListener('dragleave', this.handleDelegatedEvent);
        document.removeEventListener('drop', this.handleDelegatedEvent);
        document.removeEventListener('change', this.handleDelegatedEvent);
        document.removeEventListener('paste', this.handleGlobalPaste);

        // 清理防抖計時器
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
            this.debounceTimeout = null;
        }

        // 清空檔案
        this.clearFiles();

        this.isInitialized = false;
        console.log('🧹 FileUploadManager 資源已清理');
    };

    // 將 FileUploadManager 加入命名空間
    window.MCPFeedback.FileUploadManager = FileUploadManager;

    console.log('✅ FileUploadManager 模組載入完成');

})();
