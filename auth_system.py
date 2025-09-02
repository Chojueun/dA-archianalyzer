import streamlit as st
import json
import os
from datetime import datetime
import bcrypt
import shutil

class AuthSystem:
    def __init__(self):
        self.users_file = "users.json"
        self.user_data_dir = "user_data"
        self.load_users()
        self.ensure_user_data_directory()
    
    def ensure_user_data_directory(self):
        """사용자 데이터 디렉토리 생성"""
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
    
    def get_user_data_path(self, username):
        """사용자별 데이터 경로 반환"""
        return os.path.join(self.user_data_dir, username)
    
    def ensure_user_directory(self, username):
        """사용자별 디렉토리 생성"""
        user_path = self.get_user_data_path(username)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        return user_path
    
    def load_users(self):
        """사용자 데이터 로드"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
        else:
            self.users = {}
        
        # 기본 사용자들 자동 추가
        if "admin" not in self.users:
            self.users["admin"] = {
                "password": self.hash_password("admin123"),
                "role": "admin",
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
        
        self.save_users()
    
    def save_users(self):
        """사용자 데이터 저장"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def hash_password(self, password):
        """비밀번호 해시화"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify_password(self, password, hashed):
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def login(self, username, password):
        """로그인 처리"""
        if username in self.users and self.verify_password(password, self.users[username]["password"]):
            # 로그인 성공
            self.users[username]["last_login"] = datetime.now().isoformat()
            self.save_users()
            # 사용자 디렉토리 생성
            self.ensure_user_directory(username)
            return True
        return False
    
    def add_user(self, username, password, role="user"):
        """새 사용자 추가 (관리자만)"""
        if username not in self.users:
            self.users[username] = {
                "password": self.hash_password(password),
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
            self.save_users()
            # 사용자 디렉토리 생성
            self.ensure_user_directory(username)
            return True
        return False
    
    def remove_user(self, username):
        """사용자 삭제 (관리자만)"""
        if username in self.users and username != "admin":
            # 사용자 데이터 디렉토리 삭제
            user_data_path = self.get_user_data_path(username)
            if os.path.exists(user_data_path):
                shutil.rmtree(user_data_path)
            
            del self.users[username]
            self.save_users()
            return True
        return False
    
    def save_user_session_data(self, username, session_data):
        """사용자별 세션 데이터 영구 저장"""
        user_path = self.ensure_user_directory(username)
        session_file = os.path.join(user_path, "session_data.json")
        
        # 기존 데이터 로드
        existing_data = {}
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass
        
        # 새 데이터와 병합
        existing_data.update(session_data)
        existing_data["last_updated"] = datetime.now().isoformat()
        
        # 저장
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    def load_user_session_data(self, username):
        """사용자별 세션 데이터 로드"""
        user_path = self.get_user_data_path(username)
        session_file = os.path.join(user_path, "session_data.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_user_pdf(self, username, pdf_name, pdf_bytes):
        """사용자별 PDF 파일 저장"""
        user_path = self.ensure_user_directory(username)
        pdfs_dir = os.path.join(user_path, "pdfs")
        if not os.path.exists(pdfs_dir):
            os.makedirs(pdfs_dir)
        
        pdf_path = os.path.join(pdfs_dir, f"{pdf_name}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        return pdf_path
    
    def get_user_pdfs(self, username):
        """사용자별 PDF 파일 목록 반환"""
        user_path = self.get_user_data_path(username)
        pdfs_dir = os.path.join(user_path, "pdfs")
        
        if not os.path.exists(pdfs_dir):
            return []
        
        pdfs = []
        for file in os.listdir(pdfs_dir):
            if file.endswith('.pdf'):
                pdfs.append(file)
        return pdfs
    
    def save_user_analysis_result(self, username, analysis_name, result_data):
        """사용자별 분석 결과 저장"""
        user_path = self.ensure_user_directory(username)
        analysis_dir = os.path.join(user_path, "analysis_results")
        if not os.path.exists(analysis_dir):
            os.makedirs(analysis_dir)
        
        result_file = os.path.join(analysis_dir, f"{analysis_name}.json")
        result_data["saved_at"] = datetime.now().isoformat()
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    def get_user_analysis_results(self, username):
        """사용자별 분석 결과 목록 반환"""
        user_path = self.get_user_data_path(username)
        analysis_dir = os.path.join(user_path, "analysis_results")
        
        if not os.path.exists(analysis_dir):
            return []
        
        results = []
        for file in os.listdir(analysis_dir):
            if file.endswith('.json'):
                results.append(file.replace('.json', ''))
        return results

def init_auth():
    """인증 시스템 초기화"""
    if 'auth_system' not in st.session_state:
        st.session_state.auth_system = AuthSystem()
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

def login_page():
    """로그인 페이지"""
    st.markdown("""
    <div style="text-align: center; padding: 40px;">
        <h1 style="font-size: 2.9rem; font-weight: 900; color: #111; font-family: 'Montserrat', 'Inter', sans-serif; letter-spacing: -2px; margin-bottom: 6px; line-height: 1.13;">dAI+ ArchInsight 로그인</h1>
        <p style="font-size: 1.16rem; font-weight: 600; color: #08B89D; letter-spacing: 1.1px; font-family: 'Montserrat', 'Inter', sans-serif;">AI-driven Project Insight & Workflow</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        submit = st.form_submit_button("로그인", type="primary")
        
        if submit:
            if st.session_state.auth_system.login(username, password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("사용자명 또는 비밀번호가 올바르지 않습니다.")
    
    # 관리자 계정 정보 (개발용)
#    with st.expander("관리자 계정 정보"):
#        st.info("기본 관리자 계정: admin / admin123")

def admin_panel():
    """관리자 패널"""
    if st.session_state.current_user != "admin":
        st.error("관리자 권한이 필요합니다.")
        return
    
    st.markdown("### 👨‍💼 관리자 패널")
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["사용자 관리", "데이터 관리", "시스템 정보"])
    
    with tab1:
        # 새 사용자 추가
        with st.expander("새 사용자 추가"):
            with st.form("add_user_form"):
                new_username = st.text_input("새 사용자명")
                new_password = st.text_input("새 비밀번호", type="password")
                new_role = st.selectbox("역할", ["user", "admin"])
                add_submit = st.form_submit_button("사용자 추가")
                
                if add_submit and new_username and new_password:
                    if st.session_state.auth_system.add_user(new_username, new_password, new_role):
                        st.success(f"사용자 '{new_username}' 추가 완료!")
                    else:
                        st.error("사용자명이 이미 존재합니다.")
        
        # 사용자 목록
        with st.expander("사용자 목록"):
            users_data = []
            for username, user_info in st.session_state.auth_system.users.items():
                users_data.append({
                    "사용자명": username,
                    "역할": user_info["role"],
                    "생성일": user_info["created_at"][:10],
                    "마지막 로그인": user_info["last_login"][:10] if user_info["last_login"] else "없음"
                })
            
            if users_data:
                st.dataframe(users_data, use_container_width=True)
            
            # 사용자 삭제
            delete_username = st.text_input("삭제할 사용자명")
            if st.button("사용자 삭제", type="secondary"):
                if st.session_state.auth_system.remove_user(delete_username):
                    st.success(f"사용자 '{delete_username}' 삭제 완료!")
                    st.rerun()
                else:
                    st.error("사용자를 삭제할 수 없습니다.")
    
    with tab2:
        st.markdown("### 📊 사용자별 데이터 관리")
        
        # 사용자 선택
        user_list = list(st.session_state.auth_system.users.keys())
        selected_user = st.selectbox("사용자 선택", user_list)
        
        if selected_user:
            user_path = st.session_state.auth_system.get_user_data_path(selected_user)
            
            # 저장된 프로젝트 목록
            st.markdown("#### 📁 저장된 프로젝트")
            project_list = st.session_state.auth_system.get_user_analysis_results(selected_user)
            if project_list:
                for project in project_list:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📋 {project}")
                    with col2:
                        if st.button(f"삭제", key=f"del_proj_{project}"):
                            project_file = os.path.join(user_path, "analysis_results", f"{project}.json")
                            if os.path.exists(project_file):
                                os.remove(project_file)
                                st.success(f"프로젝트 '{project}' 삭제 완료!")
                                st.rerun()
            else:
                st.info("저장된 프로젝트가 없습니다.")
            
            # 저장된 PDF 목록
            st.markdown("#### 📄 저장된 PDF")
            pdf_list = st.session_state.auth_system.get_user_pdfs(selected_user)
            if pdf_list:
                for pdf in pdf_list:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {pdf}")
                    with col2:
                        if st.button(f"삭제", key=f"del_pdf_{pdf}"):
                            pdf_file = os.path.join(user_path, "pdfs", pdf)
                            if os.path.exists(pdf_file):
                                os.remove(pdf_file)
                                st.success(f"PDF '{pdf}' 삭제 완료!")
                                st.rerun()
            else:
                st.info("저장된 PDF가 없습니다.")
            
            # 사용자 데이터 통계
            st.markdown("#### 📈 데이터 통계")
            session_file = os.path.join(user_path, "session_data.json")
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("분석 단계", len(session_data.get("cot_history", [])))
                    with col2:
                        st.metric("저장된 프로젝트", len(project_list))
                    with col3:
                        st.metric("저장된 PDF", len(pdf_list))
                    
                    # 마지막 업데이트 시간
                    last_updated = session_data.get("last_updated", "없음")
                    if last_updated != "없음":
                        st.info(f"마지막 업데이트: {last_updated[:19]}")
                except:
                    st.warning("세션 데이터를 읽을 수 없습니다.")
            else:
                st.info("세션 데이터가 없습니다.")
    
    with tab3:
        st.markdown("### ℹ️ 시스템 정보")
        
        # 전체 사용자 통계
        total_users = len(st.session_state.auth_system.users)
        admin_users = sum(1 for user in st.session_state.auth_system.users.values() if user["role"] == "admin")
        regular_users = total_users - admin_users
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("전체 사용자", total_users)
        with col2:
            st.metric("관리자", admin_users)
        with col3:
            st.metric("일반 사용자", regular_users)
        
        # 데이터 디렉토리 정보
        st.markdown("#### 📂 데이터 디렉토리")
        user_data_dir = st.session_state.auth_system.user_data_dir
        if os.path.exists(user_data_dir):
            total_size = 0
            user_count = 0
            for user_dir in os.listdir(user_data_dir):
                user_path = os.path.join(user_data_dir, user_dir)
                if os.path.isdir(user_path):
                    user_count += 1
                    for root, dirs, files in os.walk(user_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
            
            st.info(f"사용자 데이터 디렉토리: {user_data_dir}")
            st.info(f"활성 사용자 폴더: {user_count}개")
            st.info(f"총 데이터 크기: {total_size / (1024*1024):.2f} MB")
        else:
            st.warning("사용자 데이터 디렉토리가 존재하지 않습니다.")

def logout():
    """로그아웃"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()
