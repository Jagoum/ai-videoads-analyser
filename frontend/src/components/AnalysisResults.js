import React from 'react';
import {
    Box,
    Typography,
    Grid,
    Paper,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import { Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

function AnalysisResults({ results }) {
    const {
        overall_score,
        component_scores,
        critical_issues,
        recommendations,
        deployment_decision,
    } = results;

    const chartData = {
        labels: Object.keys(component_scores).map((key) =>
            key.split('_').map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
        ),
        datasets: [
            {
                data: Object.values(component_scores),
                backgroundColor: [
                    '#4CAF50',
                    '#2196F3',
                    '#FFC107',
                    '#F44336',
                ],
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
            },
        },
    };

    return (
        <Box sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Analysis Results
            </Typography>

            <Grid container spacing={3}>
                {/* Overall Score */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>
                            Overall Score
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Doughnut data={chartData} options={chartOptions} />
                        </Box>
                    </Paper>
                </Grid>

                {/* Deployment Decision */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>
                            Deployment Status
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            {deployment_decision.ready ? (
                                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                            ) : (
                                <ErrorIcon color="error" sx={{ mr: 1 }} />
                            )}
                            <Typography>
                                {deployment_decision.ready
                                    ? 'Ready for Deployment'
                                    : 'Not Ready for Deployment'}
                            </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                            {deployment_decision.recommendation}
                        </Typography>
                    </Paper>
                </Grid>

                {/* Critical Issues */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Critical Issues
                        </Typography>
                        <List>
                            {critical_issues.length > 0 ? (
                                critical_issues.map((issue, index) => (
                                    <ListItem key={index}>
                                        <ListItemIcon>
                                            <WarningIcon color="error" />
                                        </ListItemIcon>
                                        <ListItemText primary={issue} />
                                    </ListItem>
                                ))
                            ) : (
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" />
                                    </ListItemIcon>
                                    <ListItemText primary="No critical issues found" />
                                </ListItem>
                            )}
                        </List>
                    </Paper>
                </Grid>

                {/* Recommendations */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Recommendations
                        </Typography>
                        <List>
                            {recommendations.map((rec, index) => (
                                <ListItem key={index}>
                                    <ListItemIcon>
                                        <Chip
                                            label={rec.priority}
                                            color={
                                                rec.priority === 'high'
                                                    ? 'error'
                                                    : rec.priority === 'medium'
                                                        ? 'warning'
                                                        : 'info'
                                            }
                                            size="small"
                                        />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={rec.suggestion}
                                        secondary={`Category: ${rec.category}`}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}

export default AnalysisResults;