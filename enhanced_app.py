import streamlit as st
import pandas as pd
import asyncio
import os
from datetime import datetime, timedelta

# Import enhanced components
from database import init_db, insert_task, get_tasks_by_project, get_all_projects, delete_project
from agents.orchestrator import AgentOrchestrator, AgentType
from agents.knowledge_graph import TaskKnowledgeGraph
from agents.smart_router import SmartRouter
from agents.self_healing import SelfHealingAgent
from agents.impact_tracker import impact_tracker
from agents.enterprise_logger import enterprise_logger, AuditAction
from security_config import security_manager

# Initialize enhanced system
def initialize_enhanced_system():
    """Initialize all enhanced system components"""
    
    # Initialize database
    init_db()
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register agents
    from agents.extractor import extract_tasks
    from agents.ownership import process_ownership
    from agents.ambiguity import get_ambiguous
    from agents.tracker import track_time
    from agents.summary import generate_summary
    
    orchestrator.register_agent(AgentType.EXTRACTOR, type('ExtractorAgent', (), {'extract_tasks': extract_tasks})())
    orchestrator.register_agent(AgentType.OWNERSHIP, type('OwnershipAgent', (), {'process_ownership': process_ownership})())
    orchestrator.register_agent(AgentType.AMBIGUITY, type('AmbiguityAgent', (), {'get_ambiguous': get_ambiguous})())
    orchestrator.register_agent(AgentType.TRACKER, type('TrackerAgent', (), {'track_time': track_time})())
    orchestrator.register_agent(AgentType.SUMMARY, type('SummaryAgent', (), {'generate_summary': generate_summary})())
    orchestrator.register_agent(AgentType.SELF_HEALING, SelfHealingAgent())
    
    # Initialize knowledge graph
    kg = TaskKnowledgeGraph()
    kg.build_from_database()
    
    # Initialize smart router
    router = SmartRouter()
    
    return orchestrator, kg, router

# Enhanced Streamlit application
def main():
    """Enhanced main application with all new features"""
    
    st.set_page_config(layout="wide", page_title="Enterprise AI Task Manager")
    
    # Initialize enhanced system
    orchestrator, kg, router = initialize_enhanced_system()
    
    # Security check
    if not st.session_state.get('authenticated', False):
        show_login_page()
        return
    
    # Main interface
    st.title("🧠 Enterprise Autonomous Meeting Intelligence Engine")
    
    # Sidebar with enhanced features
    with st.sidebar:
        st.header("📁 Project Management")
        
        projects = get_all_projects()
        selected_project = st.selectbox("Select Project", [""] + projects)
        new_project = st.text_input("Create New Project")
        
        project_name = new_project if new_project else selected_project
        
        if selected_project:
            if st.checkbox("Confirm Delete"):
                if st.button("Delete Project"):
                    delete_project(selected_project)
                    enterprise_logger.log_audit_event(
                        AuditAction.TASK_DELETED,
                        st.session_state.get('user_id', 'system'),
                        selected_project,
                        'project'
                    )
                    st.success("Deleted!")
        
        # Enhanced features section
        st.header("🚀 Enhanced Features")
        
        if st.button("📊 Impact Dashboard"):
            st.session_state.show_page = 'impact'
        
        if st.button("🔍 Knowledge Graph"):
            st.session_state.show_page = 'knowledge_graph'
        
        if st.button("⚙️ System Health"):
            st.session_state.show_page = 'health'
        
        if st.button("📋 Audit Logs"):
            st.session_state.show_page = 'audit'
        
        if st.button("🔐 Security"):
            st.session_state.show_page = 'security'
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.show_page = 'login'
            st.rerun()
    
    # Main content area
    page = st.session_state.get('show_page', 'main')
    
    if page == 'impact':
        show_impact_dashboard()
    elif page == 'knowledge_graph':
        show_knowledge_graph(kg)
    elif page == 'health':
        show_system_health(orchestrator, router)
    elif page == 'audit':
        show_audit_logs()
    elif page == 'security':
        show_security_status()
    else:
        show_main_interface(orchestrator, kg, router, project_name)

def show_login_page():
    """Show enhanced login page"""
    
    st.title("🔐 Enterprise Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            # Simple authentication (in production, use proper auth)
            if username and password:
                # Create secure session
                session = security_manager.create_secure_session(username)
                st.session_state.authenticated = True
                st.session_state.user_id = username
                st.session_state.session_token = session['session_token']
                st.session_state.encrypted_session = session['encrypted_session']
                
                # Log login
                enterprise_logger.log_audit_event(
                    AuditAction.USER_LOGIN,
                    username,
                    username,
                    'user'
                )
                
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def show_main_interface(orchestrator, kg, router, project_name):
    """Show enhanced main interface"""
    
    if not project_name:
        st.info("Please select or create a project")
        return
    
    # Enhanced task processing
    st.header("📝 Task Processing")
    
    transcript = st.text_area("Paste Transcript", height=200)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Run Enhanced AI Processing"):
            if transcript:
                with st.spinner("Processing with enhanced AI agents..."):
                    try:
                        # Log processing start
                        enterprise_logger.log_audit_event(
                            AuditAction.TASK_CREATED,
                            st.session_state.get('user_id', 'system'),
                            project_name,
                            'project'
                        )
                        
                        # Process with orchestrator
                        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        
                        # Use smart routing for model selection
                        selected_model, routing_info = router.route_request(
                            "task_extraction", transcript, priority="normal"
                        )
                        
                        # Record routing decision
                        impact_tracker.record_metric(
                            "model_routing_decisions", 1,
                            tags={"model": selected_model, "task_type": "task_extraction"}
                        )
                        
                        # Process workflow
                        initial_data = {"transcript": transcript, "project_name": project_name}
                        
                        # For demo, use synchronous processing
                        # In production, this would be async
                        from agents.extractor import extract_tasks
                        from agents.ownership import process_ownership
                        from agents.tracker import track_time
                        
                        tasks = extract_tasks(transcript)
                        tasks = process_ownership(tasks, project_name)
                        tasks = track_time(tasks)
                        
                        # Use knowledge graph for enhanced assignment
                        for task in tasks:
                            if task.get('owner') == 'Unassigned':
                                recommendations = kg.get_task_recommendations(task.get('task', ''))
                                if recommendations:
                                    task['suggested_owner'] = recommendations[0]['owner']
                                    task['assignment_reasoning'] = recommendations[0]['reasoning']
                        
                        # Store tasks
                        inserted_count = 0
                        duplicate_count = 0
                        
                        for task in tasks:
                            if insert_task(task, project_name):
                                inserted_count += 1
                            else:
                                duplicate_count += 1
                        
                        # Record impact metrics
                        impact_tracker.calculate_task_processing_impact(
                            len(tasks), duplicate_count
                        )
                        
                        # Log success
                        enterprise_logger.log_audit_event(
                            AuditAction.TASK_ASSIGNED,
                            st.session_state.get('user_id', 'system'),
                            project_name,
                            'project',
                            details={"tasks_processed": len(tasks), "auto_assigned": inserted_count}
                        )
                        
                        st.session_state.tasks = tasks
                        
                        st.success(f"✅ Processed {len(tasks)} tasks with {inserted_count} auto-assigned")
                        
                        if duplicate_count > 0:
                            st.info(f"⚠ {duplicate_count} duplicate tasks were skipped")
                        
                    except Exception as e:
                        # Log error
                        enterprise_logger.log_system_event(
                            "processing_error", "ERROR", str(e), "main_interface"
                        )
                        st.error(f"❌ Processing error: {str(e)}")
    
    with col2:
        if st.button("📊 Get Smart Recommendations"):
            if st.session_state.get('tasks'):
                with st.spinner("Generating recommendations..."):
                    tasks = st.session_state.tasks
                    recommendations = []
                    
                    for task in tasks:
                        if task.get('owner') == 'Unassigned':
                            task_recs = kg.get_task_recommendations(task.get('task', ''))
                            if task_recs:
                                recommendations.extend(task_recs[:2])  # Top 2 recommendations
                    
                    if recommendations:
                        st.subheader("💡 Smart Assignment Recommendations")
                        for rec in recommendations:
                            st.write(f"**{rec['owner']}** - {rec['reasoning']}")
                            st.progress(rec['confidence'])
                    else:
                        st.info("No recommendations available")
    
    # Enhanced task display
    if project_name:
        df = fetch_tasks(project_name)
        
        if not df.empty:
            st.subheader("📊 Enhanced Task View")
            
            # Add filtering options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All"] + df["status"].unique().tolist())
            
            with col2:
                owner_filter = st.selectbox("Filter by Owner", ["All"] + df["owner"].unique().tolist())
            
            with col3:
                confidence_filter = st.slider("Min Confidence", 0.0, 1.0, 0.0)
            
            # Apply filters
            filtered_df = df.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]
            if owner_filter != "All":
                filtered_df = filtered_df[filtered_df["owner"] == owner_filter]
            filtered_df = filtered_df[filtered_df["confidence"] >= confidence_filter]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Task insights
            st.subheader("📈 Task Insights")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🤖 Auto Assigned", filtered_df[filtered_df["status"] == "AUTO_ASSIGNED"].shape[0])
            
            with col2:
                st.metric("⚠ Need Clarification", filtered_df[filtered_df["status"] == "NEEDS_CLARIFICATION"].shape[0])
            
            with col3:
                st.metric("✅ Confirmed", filtered_df[filtered_df["status"] == "CONFIRMED"].shape[0])
            
            with col4:
                avg_confidence = filtered_df["confidence"].mean()
                st.metric("🎯 Avg Confidence", f"{avg_confidence:.2f}")

def show_impact_dashboard():
    """Show comprehensive impact dashboard"""
    
    st.title("📊 Impact Quantification Dashboard")
    
    # Generate dashboard
    dashboard = impact_tracker.get_kpi_dashboard()
    
    # Overall score
    st.header("🎯 Overall Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Score", f"{dashboard['overall_score']:.1f}/100")
    
    with col2:
        status = dashboard['executive_summary']['overall_performance']
        st.metric("Status", status.title())
    
    # KPI details
    st.header("📈 Key Performance Indicators")
    
    for kpi_name, kpi_data in dashboard['kpis'].items():
        with st.expander(f"📊 {kpi_name.replace('_', ' ').title()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Value", f"{kpi_data['current_value']:.2f} {kpi_data['unit']}")
            
            with col2:
                st.metric("Target", f"{kpi_data['target_value']:.2f} {kpi_data['unit']}")
            
            with col3:
                st.metric("Performance", kpi_data['performance_rating'].title())
            
            # Trend
            trend = dashboard['trends'].get(kpi_name, 'stable')
            trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}
            st.write(f"Trend: {trend_emoji.get(trend, '➡️')} {trend.title()}")
    
    # Business impact
    st.header("💰 Business Impact")
    
    business_impact = dashboard['business_impact']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cost Savings", f"${business_impact['total_cost_savings']:.2f}")
    
    with col2:
        st.metric("Time Saved", f"{business_impact['total_time_saved_hours']:.1f} hours")
    
    with col3:
        st.metric("Total Value", f"${business_impact['total_business_value']:.2f}")
    
    # Recommendations
    st.header("💡 Recommendations")
    
    recommendations = dashboard['executive_summary']['areas_for_improvement']
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.success("🎉 All KPIs are performing well!")

def show_knowledge_graph(kg):
    """Show knowledge graph insights"""
    
    st.title("🔍 Knowledge Graph Insights")
    
    # Get graph insights
    insights = kg.get_insights()
    
    # Graph statistics
    st.header("📊 Graph Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Nodes", insights['total_nodes'])
        st.metric("Total Edges", insights['total_edges'])
    
    with col2:
        st.metric("Entity Types", len(insights['entity_distribution']))
        st.metric("Connected Components", len([n for n in insights['most_connected_nodes']]))
    
    # Entity distribution
    st.header("🏷️ Entity Distribution")
    
    entity_df = pd.DataFrame(list(insights['entity_distribution'].items()), 
                           columns=['Entity Type', 'Count'])
    st.bar_chart(entity_df.set_index('Entity Type'))
    
    # Most connected nodes
    st.header("🔗 Most Connected Nodes")
    
    if insights['most_connected_nodes']:
        connected_df = pd.DataFrame(insights['most_connected_nodes'][:10], 
                                 columns=['Node', 'Centrality'])
        st.bar_chart(connected_df.set_index('Node'))
    
    # Task similarity demo
    st.header("🎯 Task Similarity Analysis")
    
    task_text = st.text_input("Enter task description to find similar tasks:")
    
    if task_text and st.button("Find Similar Tasks"):
        similar_tasks = kg.find_similar_tasks(task_text)
        
        if similar_tasks:
            st.write("Similar tasks found:")
            for task in similar_tasks:
                st.write(f"**{task['task']}** (Similarity: {task['similarity']:.2f})")
                st.write(f"Owner: {task['owner']} | Status: {task['status']}")
                st.write("---")
        else:
            st.info("No similar tasks found")

def show_system_health(orchestrator, router):
    """Show system health monitoring"""
    
    st.title("🏥 System Health Monitor")
    
    # Agent performance
    st.header("🤖 Agent Performance")
    
    agent_metrics = orchestrator.get_agent_metrics()
    
    for agent_name, metrics in agent_metrics.items():
        with st.expander(f"📊 {agent_name.replace('_', ' ').title()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Tasks Processed", metrics['tasks_processed'])
            
            with col2:
                st.metric("Success Rate", f"{metrics['success_rate']:.2%}")
            
            with col3:
                st.metric("Avg Time", f"{metrics['avg_processing_time']:.2f}s")
    
    # Router performance
    st.header("🛣️ Smart Router Performance")
    
    router_report = router.get_performance_report()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Calls", router_report['total_calls'])
        st.metric("Total Cost", f"${router_report['total_cost']:.4f}")
    
    with col2:
        st.metric("Avg Response Time", f"{router_report['avg_response_time']:.2f}s")
    
    # Cost optimization suggestions
    st.header("💡 Cost Optimization")
    
    suggestions = router.get_cost_optimization_suggestions()
    
    if suggestions:
        for suggestion in suggestions:
            if suggestion['type'] == 'cost_optimization':
                st.warning(f"💰 {suggestion['suggestion']}")
                st.write(f"Potential savings: {suggestion['potential_savings']}")
            elif suggestion['type'] == 'budget_warning':
                st.error(f"⚠️ {suggestion['period'].title()} budget usage: {suggestion['usage_percentage']:.1%}")
    else:
        st.success("🎉 No optimization suggestions needed!")

def show_audit_logs():
    """Show audit logs"""
    
    st.title("📋 Audit Logs")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_filter = st.selectbox("Filter by Action", ["All"] + [a.value for a in AuditAction])
    
    with col2:
        days_back = st.selectbox("Time Period", [1, 7, 30, 90])
    
    with col3:
        limit = st.selectbox("Limit", [10, 50, 100, 500])
    
    # Get audit trail
    start_date = datetime.now() - timedelta(days=days_back)
    
    audit_trail = enterprise_logger.get_audit_trail(
        action=AuditAction(action_filter) if action_filter != "All" else None,
        start_date=start_date,
        limit=limit
    )
    
    if audit_trail:
        # Convert to DataFrame
        df = pd.DataFrame(audit_trail)
        
        # Format timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Display
        st.dataframe(df[['timestamp', 'action', 'user_id', 'resource_type', 'outcome', 'risk_level']], 
                    use_container_width=True)
        
        # Export option
        if st.button("📥 Export Audit Logs"):
            export_data = enterprise_logger.export_audit_logs(start_date, datetime.now())
            st.download_button(
                label="Download JSON",
                data=export_data,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    else:
        st.info("No audit logs found for selected criteria")

def show_security_status():
    """Show security configuration status"""
    
    st.title("🔐 Security Status")
    
    # Get security audit
    security_audit = security_manager.get_security_audit_config()
    
    # Security metrics
    st.header("🛡️ Security Configuration")
    
    for key, value in security_audit.items():
        if isinstance(value, bool):
            status = "✅ Enabled" if value else "❌ Disabled"
            st.metric(key.replace('_', ' ').title(), status)
        else:
            st.metric(key.replace('_', ' ').title(), value)
    
    # Security recommendations
    st.header("💡 Security Recommendations")
    
    recommendations = []
    
    if not security_audit['encryption_enabled']:
        recommendations.append("Enable encryption for sensitive data")
    
    if not security_audit['audit_logging']:
        recommendations.append("Enable audit logging for compliance")
    
    if not security_audit['require_mfa']:
        recommendations.append("Enable multi-factor authentication")
    
    if security_audit['password_min_length'] < 12:
        recommendations.append("Increase minimum password length to 12 characters")
    
    if recommendations:
        for rec in recommendations:
            st.warning(f"⚠️ {rec}")
    else:
        st.success("🎉 Security configuration is optimal!")

def fetch_tasks(project_name):
    """Fetch tasks for project"""
    from database import get_tasks_by_project
    rows = get_tasks_by_project(project_name)
    return pd.DataFrame(rows, columns=[
        "task", "owner", "deadline", "status", "confidence", "message", "project", "last_updated"
    ])

if __name__ == "__main__":
    main()
