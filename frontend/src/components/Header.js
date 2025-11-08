import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';
import MovieFilterIcon from '@mui/icons-material/MovieFilter';

function Header() {
    return (
        <AppBar position="static">
            <Toolbar>
                <MovieFilterIcon sx={{ mr: 2 }} />
                <Typography variant="h6" component="div">
                    AI Video Ads Analyzer
                </Typography>
            </Toolbar>
        </AppBar>
    );
}

export default Header;