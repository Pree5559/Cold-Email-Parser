import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class AnalyticsDashboard:
    """Generate analytics and visualizations for cold email campaigns."""
    
    def __init__(self, database):
        """Initialize analytics dashboard.
        
        Args:
            database: Database instance
        """
        self.db = database
    
    def get_overview_stats(self) -> Dict:
        """Get overview statistics.
        
        Returns:
            Dictionary with overview statistics
        """
        stats = self.db.get_statistics()
        
        return {
            "total_contacts": stats['total_contacts'],
            "total_emails_sent": stats['logs_by_status'].get('sent', 0),
            "total_emails_skipped": stats['logs_by_status'].get('skipped', 0),
            "total_emails_failed": stats['logs_by_status'].get('failed', 0),
            "success_rate": stats['success_rate'],
            "average_quality_score": stats['average_quality_score'],
            "contacts_by_status": stats['contacts_by_status']
        }
    
    def get_time_series_data(self, days: int = 30) -> pd.DataFrame:
        """Get time series data for the last N days.
        
        Args:
            days: Number of days to include
            
        Returns:
            DataFrame with time series data
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            return pd.DataFrame()
        
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Filter to last N days
        cutoff_date = datetime.now().date() - timedelta(days=days)
        df = df[df['date'] >= cutoff_date]
        
        # Group by date and status
        daily_stats = df.groupby(['date', 'status']).size().unstack(fill_value=0)
        
        return daily_stats
    
    def create_time_series_chart(self, days: int = 30) -> go.Figure:
        """Create time series chart of email activity.
        
        Args:
            days: Number of days to include
            
        Returns:
            Plotly figure
        """
        df = self.get_time_series_data(days)
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected time period",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        fig = go.Figure()
        
        # Add traces for each status
        colors = {'sent': '#28a745', 'skipped': '#ffc107', 'failed': '#dc3545'}
        
        for status in ['sent', 'skipped', 'failed']:
            if status in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[status],
                    mode='lines+markers',
                    name=status.capitalize(),
                    line=dict(color=colors.get(status, '#1f77b4')),
                    stackgroup='one'
                ))
        
        fig.update_layout(
            title=f"Email Activity - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Number of Emails",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_status_pie_chart(self) -> go.Figure:
        """Create pie chart of email status distribution.
        
        Returns:
            Plotly figure
        """
        stats = self.db.get_statistics()
        logs_by_status = stats['logs_by_status']
        
        if not logs_by_status:
            fig = go.Figure()
            fig.add_annotation(
                text="No email data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        labels = list(logs_by_status.keys())
        values = list(logs_by_status.values())
        
        colors = {'sent': '#28a745', 'skipped': '#ffc107', 'failed': '#dc3545'}
        pie_colors = [colors.get(label, '#1f77b4') for label in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=[label.capitalize() for label in labels],
            values=values,
            marker=dict(colors=pie_colors),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Email Status Distribution",
            template='plotly_white'
        )
        
        return fig
    
    def create_quality_score_chart(self) -> go.Figure:
        """Create histogram of quality scores.
        
        Returns:
            Plotly figure
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            fig = go.Figure()
            fig.add_annotation(
                text="No quality score data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        df = pd.DataFrame(logs)
        df = df[df['quality_score'].notna()]
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No quality score data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        fig = go.Figure(data=[go.Histogram(
            x=df['quality_score'],
            nbinsx=20,
            marker_color='#1f77b4'
        )])
        
        fig.update_layout(
            title="Email Quality Score Distribution",
            xaxis_title="Quality Score",
            yaxis_title="Count",
            template='plotly_white'
        )
        
        return fig
    
    def create_company_chart(self, top_n: int = 10) -> go.Figure:
        """Create bar chart of emails sent by company.
        
        Args:
            top_n: Number of top companies to show
            
        Returns:
            Plotly figure
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            fig = go.Figure()
            fig.add_annotation(
                text="No email data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        df = pd.DataFrame(logs)
        
        # Join with contacts to get company info
        contacts_df = pd.DataFrame(self.db.get_all_contacts(limit=10000))
        
        if contacts_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No contact data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        merged = df.merge(contacts_df, left_on='contact_id', right_on='id')
        
        # Count by company
        company_counts = merged['company'].value_counts().head(top_n)
        
        fig = go.Figure(data=[go.Bar(
            x=company_counts.index,
            y=company_counts.values,
            marker_color='#1f77b4'
        )])
        
        fig.update_layout(
            title=f"Top {top_n} Companies by Email Volume",
            xaxis_title="Company",
            yaxis_title="Number of Emails",
            template='plotly_white'
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_template_performance_chart(self) -> go.Figure:
        """Create bar chart of template performance.
        
        Returns:
            Plotly figure
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            fig = go.Figure()
            fig.add_annotation(
                text="No template data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        df = pd.DataFrame(logs)
        df = df[df['template_used'].notna()]
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No template data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Calculate success rate by template
        template_stats = df.groupby('template_used').agg({
            'status': lambda x: (x == 'sent').mean() * 100,
            'id': 'count'
        }).rename(columns={'status': 'success_rate', 'id': 'count'})
        
        fig = go.Figure(data=[go.Bar(
            x=template_stats.index,
            y=template_stats['success_rate'],
            marker_color='#1f77b4',
            text=template_stats['count'].apply(lambda x: f"({x} emails)"),
            textposition='outside'
        )])
        
        fig.update_layout(
            title="Template Success Rate",
            xaxis_title="Template",
            yaxis_title="Success Rate (%)",
            template='plotly_white'
        )
        
        return fig
    
    def create_word_count_chart(self) -> go.Figure:
        """Create scatter plot of word count vs quality score.
        
        Returns:
            Plotly figure
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            fig = go.Figure()
            fig.add_annotation(
                text="No email data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        df = pd.DataFrame(logs)
        df = df[(df['word_count'].notna()) & (df['quality_score'].notna())]
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No word count or quality score data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Color by status
        colors = {'sent': '#28a745', 'skipped': '#ffc107', 'failed': '#dc3545'}
        df['color'] = df['status'].map(colors).fillna('#1f77b4')
        
        fig = go.Figure(data=[go.Scatter(
            x=df['word_count'],
            y=df['quality_score'],
            mode='markers',
            marker=dict(
                color=df['color'],
                size=10,
                opacity=0.7
            ),
            text=df['status'].apply(lambda x: x.capitalize()),
            hovertemplate='Word Count: %{x}<br>Quality Score: %{y}<br>Status: %{text}'
        )])
        
        fig.update_layout(
            title="Word Count vs Quality Score",
            xaxis_title="Word Count",
            yaxis_title="Quality Score",
            template='plotly_white'
        )
        
        return fig
    
    def get_detailed_metrics(self) -> Dict:
        """Get detailed metrics for analytics.
        
        Returns:
            Dictionary with detailed metrics
        """
        logs = self.db.get_logs(limit=10000)
        
        if not logs:
            return {}
        
        df = pd.DataFrame(logs)
        
        metrics = {
            'total_emails': len(df),
            'average_word_count': df['word_count'].mean() if 'word_count' in df.columns else 0,
            'median_word_count': df['word_count'].median() if 'word_count' in df.columns else 0,
            'average_quality_score': df['quality_score'].mean() if 'quality_score' in df.columns else 0,
            'median_quality_score': df['quality_score'].median() if 'quality_score' in df.columns else 0,
        }
        
        # Spam risk distribution
        if 'spam_risk' in df.columns:
            spam_dist = df['spam_risk'].value_counts().to_dict()
            metrics['spam_risk_distribution'] = spam_dist
        
        # Template usage
        if 'template_used' in df.columns:
            template_usage = df['template_used'].value_counts().to_dict()
            metrics['template_usage'] = template_usage
        
        return metrics
    
    def export_analytics_report(self, output_path: str) -> bool:
        """Export analytics report to CSV.
        
        Args:
            output_path: Path for the output file
            
        Returns:
            True if export was successful
        """
        try:
            logs = self.db.get_logs(limit=10000)
            
            if not logs:
                return False
            
            df = pd.DataFrame(logs)
            df.to_csv(output_path, index=False)
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
