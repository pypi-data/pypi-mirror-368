"""
edaflow.display - Universal Notebook Display Optimization
========================================================

Automatically detects notebook environment (Jupyter, Colab, VS Code) and 
applies optimal styling for better visibility across different themes.

Main Functions:
- optimize_display(): One-function solution for universal compatibility
"""

import os
import sys
from typing import Dict, List, Optional, Union

def optimize_display(
    theme: Optional[str] = None,
    high_contrast: bool = False,
    apply_matplotlib: bool = True,
    verbose: bool = True,
    clean_output: bool = True
) -> Dict[str, Union[str, bool, List[str]]]:
    """
    🎯 Optimize edaflow display for any notebook environment.
    
    Automatically detects platform (Jupyter, Colab, VS Code) and theme,
    then applies CSS fixes and matplotlib configuration for improved visibility.
    
    Parameters:
    -----------
    theme : str, optional
        Force specific theme ('light', 'dark', 'auto'). If None, auto-detects.
    high_contrast : bool, default False
        Enable high contrast mode for accessibility.
    apply_matplotlib : bool, default True
        Configure matplotlib for better plot visibility.  
    verbose : bool, default True
        Show detection results and applied optimizations.
    clean_output : bool, default True
        Use clean HTML output in Colab for better readability.
    
    Returns:
    --------
    dict : Configuration details and applied optimizations
    
    Examples:
    ---------
    >>> import edaflow
    >>> edaflow.optimize_display()  # Auto-detect and optimize
    ✅ Display optimized for Google Colab (dark theme)
    � edaflow functions should now display with improved visibility
    
    >>> edaflow.optimize_display(theme='dark', high_contrast=True)  # Custom
    ✅ Display optimized for VS Code (dark theme)
    🎨 High contrast mode: ENABLED
    � edaflow functions should now display with improved visibility
    """
    
    # 1. DETECT PLATFORM AND THEME
    platform_info = _detect_notebook_platform()
    
    if theme:
        final_theme = theme
        if verbose:
            print(f"🎯 Theme set to: {final_theme}")
    else:
        final_theme = platform_info['detected_theme']
        if verbose:
            print(f"🔍 Auto-detected: {platform_info['platform']} ({final_theme} theme)")
    
    # 2. APPLY CSS OPTIMIZATIONS
    try:
        _apply_css_optimizations(platform_info['platform'], final_theme, high_contrast)
        css_applied = True
    except Exception as e:
        if verbose:
            print(f"⚠️  CSS application failed: {e}")
        css_applied = False
    
    # 3. CONFIGURE MATPLOTLIB
    matplotlib_configured = False
    if apply_matplotlib:
        try:
            _configure_matplotlib_theme(platform_info['platform'], final_theme, high_contrast)
            matplotlib_configured = True
        except Exception as e:
            if verbose:
                print(f"⚠️  Matplotlib configuration failed: {e}")
    
    # 4. SET UP COLORS
    color_config = _setup_color_palette(final_theme, high_contrast, platform_info['platform'])
    
    # 5. DISPLAY RESULTS
    result = {
        'platform': platform_info['platform'],
        'theme': final_theme,
        'high_contrast': high_contrast,
        'css_applied': css_applied,
        'matplotlib_configured': matplotlib_configured,
        'optimizations': platform_info.get('features', [])
    }
    
    if verbose:
        if clean_output and platform_info['platform'] == 'Google Colab':
            _display_clean_colab_output(result)
        else:
            # Traditional text output
            print(f"✅ Display optimized for {platform_info['platform']} ({final_theme} theme)")
            if high_contrast:
                print("🎨 High contrast mode: ENABLED")
            print("� edaflow functions should now display with improved visibility")
    
    return result


def _detect_notebook_platform() -> Dict[str, Union[str, List[str]]]:
    """
    Detect current notebook platform and theme.
    
    Returns:
    --------
    dict : Platform detection results
    """
    result = {
        'platform': 'unknown',
        'detected_theme': 'auto',
        'confidence': 'low',
        'features': []
    }
    
    try:
        # METHOD 1: Google Colab Detection
        if _is_google_colab():
            result.update({
                'platform': 'Google Colab',
                'detected_theme': _detect_colab_theme(),  # Dynamic detection
                'confidence': 'high',
                'features': ['colab_css', 'mobile_friendly', 'google_colors']
            })
            return result
    except Exception:
        pass
    
    try:
        # METHOD 2: VS Code Detection
        if _is_vscode():
            result.update({
                'platform': 'VS Code',
                'detected_theme': 'auto',
                'confidence': 'high', 
                'features': ['vscode_css', 'theme_adaptive', 'editor_integration']
            })
            return result
    except Exception:
        pass
    
    try:
        # METHOD 3: JupyterLab Detection
        if _is_jupyter_environment():
            result.update({
                'platform': 'JupyterLab',
                'detected_theme': 'auto',
                'confidence': 'medium',
                'features': ['jupyter_css', 'theme_detection', 'universal_colors']
            })
            return result
    except Exception:
        pass
    
    # METHOD 4: Safe Fallback
    result.update({
        'platform': 'Notebook Environment',
        'detected_theme': 'auto',
        'confidence': 'low',
        'features': ['universal_css', 'safe_colors']
    })
    
    return result


def _is_google_colab() -> bool:
    """Check if running in Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        try:
            # Alternative detection method
            from IPython import get_ipython
            return 'google.colab' in str(get_ipython())
        except Exception:
            return False


def _detect_colab_theme() -> str:
    """
    Detect Google Colab theme more accurately.
    
    Returns:
        str: 'dark', 'light', or 'auto'
    """
    try:
        # Method 1: Check environment variables for theme hints
        import os
        theme_hint = os.environ.get('COLAB_THEME', '').lower()
        if theme_hint in ['dark', 'light']:
            return theme_hint
            
        # Method 2: Try JavaScript-based detection
        try:
            from IPython.display import Javascript, display
            import time
            
            # Use JavaScript to detect theme from Colab's DOM/CSS
            js_code = """
            function detectColabTheme() {
                // Method 1: Check computed styles on body
                const body = document.body;
                const computedStyle = getComputedStyle(body);
                const bgColor = computedStyle.backgroundColor;
                
                // Method 2: Check for dark theme indicators
                const isDarkByColor = bgColor === 'rgb(66, 66, 66)' || 
                                     bgColor === 'rgb(48, 48, 48)' ||
                                     bgColor === 'rgb(32, 32, 32)';
                
                // Method 3: Check CSS classes
                const isDarkByClass = body.classList.contains('theme-dark') ||
                                     body.classList.contains('dark') ||
                                     document.documentElement.classList.contains('dark');
                
                // Method 4: Check media query preference
                const prefersDark = window.matchMedia && 
                                  window.matchMedia('(prefers-color-scheme: dark)').matches;
                
                // Combine all detection methods
                const isDark = isDarkByColor || isDarkByClass || prefersDark;
                
                // Store in a way Python can access (though this is tricky)
                window._colabThemeDetected = isDark ? 'dark' : 'light';
                
                // Also try to set a cookie for persistence
                document.cookie = `colab_theme=${isDark ? 'dark' : 'light'};path=/`;
                
                return isDark ? 'dark' : 'light';
            }
            
            detectColabTheme();
            """
            
            # Execute the JavaScript (silently)
            display(Javascript(js_code))
            time.sleep(0.1)  # Give JS time to execute
            
            # Try to read back the result from cookie
            import http.cookies
            cookies = http.cookies.SimpleCookie()
            cookie_header = os.environ.get('HTTP_COOKIE', '')
            if cookie_header:
                cookies.load(cookie_header)
                if 'colab_theme' in cookies:
                    detected_theme = cookies['colab_theme'].value
                    if detected_theme in ['dark', 'light']:
                        return detected_theme
                        
        except Exception:
            pass
            
        # Method 3: Try to infer from user preferences or system settings
        try:
            # Check if running in dark mode based on system preferences
            # This is platform-specific and may not always work
            if hasattr(os, 'environ'):
                # Check common dark mode environment variables
                dark_indicators = [
                    os.environ.get('THEME', '').lower() == 'dark',
                    os.environ.get('COLOR_SCHEME', '').lower() == 'dark',
                    'dark' in os.environ.get('TERM', '').lower()
                ]
                if any(dark_indicators):
                    return 'dark'
                    
        except Exception:
            pass
        
    except Exception:
        pass
    
    # Default to 'auto' for better theme adaptation - let CSS handle it
    return 'auto'


def _is_vscode() -> bool:
    """Check if running in VS Code."""
    return bool(
        os.environ.get('VSCODE_PID') or 
        'vscode' in os.environ.get('TERM_PROGRAM', '').lower()
    )


def _is_jupyter_environment() -> bool:
    """Check if running in Jupyter environment."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except Exception:
        return False


def _apply_css_optimizations(platform: str, theme: str, high_contrast: bool) -> None:
    """
    Apply CSS fixes for the detected platform.
    
    Parameters:
    -----------
    platform : str
        Detected platform name
    theme : str  
        Detected or forced theme
    high_contrast : bool
        Whether high contrast mode is enabled
    """
    try:
        from IPython.display import HTML, display
    except ImportError:
        # Not in IPython environment, skip CSS injection
        return
    
    # Universal CSS base with dynamic theme detection
    css = '''
    <style>
    /* edaflow universal display optimizations with dynamic theme support */
    
    /* Auto theme detection using CSS selectors and media queries */
    .jp-OutputArea-output pre,
    .output pre,
    .output_text pre {
        border: 1px solid #ccc;
        padding: 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        line-height: 1.4;
        transition: background-color 0.3s, color 0.3s, border-color 0.3s;
    }
    
    /* Dynamic theme detection for dark mode */
    @media (prefers-color-scheme: dark),
    [data-jp-theme-name*="Dark"] *,
    [data-jp-theme-name*="dark"] *,
    .theme-dark *,
    body[style*="rgb(66, 66, 66)"] *,
    body[style*="rgb(48, 48, 48)"] * {
        --bg-color: rgba(40, 40, 40, 0.9);
        --text-color: #E8E8E8;
        --border-color: #666666;
    }
    
    /* Dynamic theme detection for light mode */
    @media (prefers-color-scheme: light),
    [data-jp-theme-name*="Light"] *,
    [data-jp-theme-name*="light"] *,
    .theme-light *,
    body:not([style*="rgb(66, 66, 66)"]):not([style*="rgb(48, 48, 48)"]) * {
        --bg-color: rgba(248, 248, 248, 0.9);
        --text-color: #333333;
        --border-color: #CCCCCC;
    }
    
    /* Apply the dynamic theme variables */
    .jp-OutputArea-output pre,
    .output pre,
    .output_text pre {
        background-color: var(--bg-color, transparent) !important;
        color: var(--text-color, inherit) !important;
        border-color: var(--border-color, #ccc) !important;
    }
    
    
    .jp-OutputArea-output table,
    .output table,
    .output_html table {
        background-color: transparent !important;
        border-collapse: collapse !important;
        width: 100%;
        margin: 10px 0;
    }
    
    .jp-OutputArea-output table th,
    .output table th,
    .output_html table th {
        background-color: #f0f0f0 !important;
        padding: 8px;
        border: 1px solid #ccc;
        font-weight: bold;
    }
    
    .jp-OutputArea-output table td,
    .output table td,
    .output_html table td {
        padding: 8px;
        border: 1px solid #ccc;
    }
    '''
    
    # Platform-specific CSS
    if platform == 'Google Colab':
        css += '''
    /* Google Colab specific optimizations */
    .output_text {
        font-family: 'Roboto Mono', 'Courier New', monospace !important;
    }
    
    .output_html table th {
        background-color: #e8f0fe !important;
        color: #1a73e8 !important;
    }
    
    /* Rich console output fixes for Google Colab */
    pre[style*="color"] {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        line-height: 1.4 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-x: hidden !important;
        padding: 8px 12px !important;
        border-radius: 4px !important;
        margin: 4px 0 !important;
    }
    
    /* Fix Rich panel alignment and borders in Colab */
    pre[style*="border"] {
        border-style: solid !important;
        border-width: 1px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Rich table styling improvements for Colab */
    pre table, 
    pre[style*="table"] {
        border-collapse: separate !important;
        border-spacing: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        table-layout: fixed !important;
    }
    
    /* Ensure proper text wrapping in Rich panels */
    pre[style*="│"] {
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    '''
    
    elif platform == 'VS Code':
        css += '''
    /* VS Code specific optimizations */
    .vscode-dark .output,
    .vscode-dark .jp-OutputArea-output {
        color: #CCCCCC !important;
    }
    
    .vscode-light .output,
    .vscode-light .jp-OutputArea-output {
        color: #333333 !important;
    }
    '''
    
    else:  # JupyterLab and others
        css += '''
    /* JupyterLab theme detection */
    [data-jp-theme-name*="Dark"] .jp-OutputArea-output,
    [data-jp-theme-name*="dark"] .jp-OutputArea-output {
        color: #FFFFFF !important;
    }
    
    [data-jp-theme-name*="Light"] .jp-OutputArea-output,
    [data-jp-theme-name*="light"] .jp-OutputArea-output {
        color: #000000 !important;
    }
    '''
    
    # Theme-specific adjustments
    if theme == 'dark':
        css += '''
    /* Dark theme specific fixes */
    .jp-OutputArea-output,
    .output {
        color: #FFFFFF !important;
    }
    
    .jp-OutputArea-output table th,
    .output table th {
        background-color: #333333 !important;
        color: #FFFFFF !important;
        border-color: #666666 !important;
    }
    
    .jp-OutputArea-output table td,
    .output table td {
        border-color: #666666 !important;
    }
    '''
    
    # High contrast mode
    if high_contrast:
        css += '''
    /* High contrast accessibility mode */
    .jp-OutputArea-output,
    .output {
        filter: contrast(1.4) brightness(1.2) !important;
        font-weight: 500 !important;
    }
    
    .jp-OutputArea-output table,
    .output table {
        border: 2px solid #000000 !important;
    }
    '''
    
    css += '''
    </style>
    '''
    
    # Apply the CSS
    display(HTML(css))


def _configure_matplotlib_theme(platform: str, theme: str, high_contrast: bool) -> None:
    """
    Configure matplotlib for optimal visibility.
    
    Parameters:
    -----------
    platform : str
        Detected platform name
    theme : str
        Detected or forced theme
    high_contrast : bool
        Whether high contrast mode is enabled
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    
    # Platform-specific DPI settings
    platform_configs = {
        'Google Colab': {
            'figure.dpi': 100,
            'savefig.dpi': 150,
            'figure.figsize': (10, 6)
        },
        'VS Code': {
            'figure.dpi': 96,
            'figure.figsize': (10, 6)
        },
        'JupyterLab': {
            'figure.dpi': 100,
            'figure.figsize': (8, 5)
        }
    }
    
    # Apply platform-specific settings
    config = platform_configs.get(platform, platform_configs['JupyterLab'])
    plt.rcParams.update(config)
    
    # Universal theme settings
    if theme in ['dark', 'auto']:
        plt.rcParams.update({
            'figure.facecolor': 'none',      # Transparent background
            'axes.facecolor': 'none',        # Transparent axes
            'axes.edgecolor': '#CCCCCC',     # Light edges
            'axes.labelcolor': '#CCCCCC',    # Light labels
            'text.color': '#CCCCCC',         # Light text
            'xtick.color': '#CCCCCC',        # Light x-axis ticks
            'ytick.color': '#CCCCCC',        # Light y-axis ticks
            'grid.color': '#666666',         # Gray grid
            'grid.alpha': 0.3,               # Semi-transparent grid
        })
    else:  # Light theme
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#333333',
            'axes.labelcolor': '#333333', 
            'text.color': '#333333',
            'xtick.color': '#333333',
            'ytick.color': '#333333',
            'grid.color': '#CCCCCC',
            'grid.alpha': 0.5,
        })
    
    # Set color palette
    try:
        import seaborn as sns
        colors = _get_platform_colors(platform, theme, high_contrast)
        sns.set_palette(colors)
    except ImportError:
        pass


def _setup_color_palette(theme: str, high_contrast: bool, platform: str) -> Dict[str, str]:
    """
    Set up adaptive color schemes.
    
    Parameters:
    -----------
    theme : str
        Theme name
    high_contrast : bool
        High contrast mode flag
    platform : str
        Platform name
        
    Returns:
    --------
    dict : Color configuration
    """
    # Platform-specific color schemes
    platform_colors = {
        'Google Colab': {
            'light': {'primary': '#4285F4', 'secondary': '#34A853'},
            'dark': {'primary': '#8AB4F8', 'secondary': '#81C995'}
        },
        'VS Code': {
            'light': {'primary': '#007ACC', 'secondary': '#28A745'},
            'dark': {'primary': '#3794FF', 'secondary': '#4EC9B0'}
        },
        'JupyterLab': {
            'light': {'primary': '#2196F3', 'secondary': '#4CAF50'},
            'dark': {'primary': '#64B5F6', 'secondary': '#81C784'}
        }
    }
    
    # Get base colors for platform and theme
    colors = platform_colors.get(platform, platform_colors['JupyterLab'])
    color_set = colors.get(theme, colors.get('light', {'primary': '#2196F3', 'secondary': '#4CAF50'}))
    
    # Apply high contrast adjustments
    if high_contrast:
        if theme == 'dark':
            color_set.update({
                'primary': '#00FF88',
                'secondary': '#FF6666'
            })
        else:
            color_set.update({
                'primary': '#0044AA', 
                'secondary': '#CC0000'
            })
    
    return color_set


def _get_platform_colors(platform: str, theme: str, high_contrast: bool) -> List[str]:
    """
    Get color palette for matplotlib/seaborn.
    
    Returns:
    --------
    list : Color palette as hex codes
    """
    if high_contrast:
        # Ultra-bright colors for accessibility
        return ['#FF0080', '#00FF80', '#8000FF', '#FFFF00', '#00FFFF', '#FF4000']
    
    elif platform == 'Google Colab':
        # Google brand colors
        return ['#4285F4', '#34A853', '#FBBC04', '#EA4335', '#9C27B0', '#FF9800']
    
    elif platform == 'VS Code':
        # VS Code compatible colors
        return ['#007ACC', '#28A745', '#FFC107', '#DC3545', '#6F42C1', '#FD7E14']
    
    else:
        # Universal bright colors for dark themes
        return ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']


def _display_clean_colab_output(result: Dict[str, Union[str, bool, List[str]]]) -> None:
    """Display optimization results in a clean, Colab-friendly format."""
    try:
        from IPython.display import HTML, display
        
        # Extract key information
        platform = result.get('platform', 'Unknown')
        theme = result.get('theme', 'auto')
        high_contrast = result.get('high_contrast', False)
        css_applied = result.get('css_applied', False)
        matplotlib_configured = result.get('matplotlib_configured', False)
        
        # Choose colors based on detected theme
        if theme == 'dark':
            bg_color = '#2d3748'
            text_color = '#e2e8f0'
            success_color = '#48bb78'
            info_color = '#4299e1'
        else:
            bg_color = '#f7fafc'
            text_color = '#2d3748'
            success_color = '#38a169'
            info_color = '#3182ce'
        
        # Create clean HTML display
        html = f"""
        <div style="
            background: {bg_color};
            color: {text_color};
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid {success_color};
            margin: 10px 0;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
        ">
            <h3 style="margin: 0 0 10px 0; color: {success_color};">
                ✅ Display Optimization Complete
            </h3>
            
            <div style="margin: 8px 0;">
                <span style="color: {info_color}; font-weight: bold;">📱 Platform:</span> {platform}
            </div>
            
            <div style="margin: 8px 0;">
                <span style="color: {info_color}; font-weight: bold;">🎨 Theme:</span> {theme.title()}
                {' (High Contrast)' if high_contrast else ''}
            </div>
            
            <div style="margin: 8px 0;">
                <span style="color: {info_color}; font-weight: bold;">🔧 Status:</span>
                {'✅ CSS Applied' if css_applied else '❌ CSS Failed'} • 
                {'✅ Matplotlib Configured' if matplotlib_configured else '❌ Matplotlib Failed'}
            </div>
            
            <div style="margin-top: 12px; font-style: italic; opacity: 0.8;">
                � edaflow functions should now display with improved visibility
            </div>
        </div>
        """
        
        display(HTML(html))
        
    except Exception:
        # Fallback to regular text output
        print(f"✅ Display optimized for {platform} ({theme} theme)")
        if high_contrast:
            print("🎨 High contrast mode: ENABLED")
        print("� edaflow functions should now display with improved visibility")


# Export main function
__all__ = ['optimize_display']
