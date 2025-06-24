---
title: Color Grading Guide
description: Professional color grading techniques and workflows for video enhancement
---

# Color Grading Guide

Master the art of professional color grading with the VFX MCP Server. This comprehensive guide covers everything from basic color correction to advanced creative grading techniques used in professional video production.

## 🎨 Introduction to Color Grading

Color grading is the process of enhancing or altering the color and luminance of video footage to achieve a specific aesthetic or to correct technical issues. It's divided into two main phases:

1. **Color Correction**: Fixing technical issues and achieving a neutral, balanced look
2. **Color Grading**: Creative enhancement to achieve a specific mood or style

### Understanding Color Theory

Before diving into techniques, let's understand the key color properties:

- **Brightness**: Overall luminance or exposure level
- **Contrast**: Difference between light and dark areas
- **Saturation**: Intensity or purity of colors
- **Temperature**: Warmth (orange) vs coolness (blue) of the image
- **Tint**: Green vs magenta color cast
- **Gamma**: Midtone brightness and contrast curve
- **Shadows/Highlights**: Specific adjustments to dark and bright areas

## 🔧 Basic Color Correction Workflow

### Step 1: Technical Analysis

Always start by analyzing your footage to understand what needs correction:

```python
async def analyze_footage_for_correction(video_path: str):
    """Analyze video to determine color correction needs"""
    
    # Get video information
    info = await session.call_tool("get_video_info", {
        "video_path": video_path
    })
    
    print(f"📹 Analyzing: {video_path}")
    print(f"Duration: {info['duration']}s")
    print(f"Resolution: {info['width']}x{info['height']}")
    print(f"Format: {info['format']}")
    
    # Extract dominant colors for analysis
    color_analysis = await session.call_tool("extract_dominant_colors", {
        "input_path": video_path,
        "num_colors": 8,
        "sample_interval": 10.0
    })
    
    print(f"\n🎨 Color Analysis:")
    for i, color_info in enumerate(color_analysis['dominant_colors']):
        print(f"  Color {i+1}: {color_info['hex']} ({color_info['percentage']:.1f}%)")
    
    # Check for common issues
    issues = []
    recommendations = {}
    
    # Analyze color temperature (simplified)
    warm_colors = sum(c['percentage'] for c in color_analysis['dominant_colors'] 
                     if any(warm in c['hex'].lower() for warm in ['ff', 'ee', 'dd']))
    
    if warm_colors > 60:
        issues.append("Image appears warm/orange")
        recommendations['temperature'] = -0.2
    elif warm_colors < 20:
        issues.append("Image appears cool/blue")
        recommendations['temperature'] = 0.2
    
    # Basic recommendations
    recommendations.update({
        'brightness': 0.02,  # Slight brightness boost
        'contrast': 1.05,    # Minimal contrast increase
        'saturation': 1.0    # Keep natural saturation
    })
    
    print(f"\n🔍 Issues detected: {len(issues)}")
    for issue in issues:
        print(f"  ⚠️  {issue}")
    
    print(f"\n💡 Recommendations:")
    for param, value in recommendations.items():
        print(f"  {param}: {value}")
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'color_analysis': color_analysis
    }

# Usage
analysis = await analyze_footage_for_correction("raw_footage.mp4")
```

### Step 2: Basic Color Correction

Apply fundamental corrections to achieve a neutral, balanced image:

```python
async def basic_color_correction(input_path: str, output_path: str, analysis_data=None):
    """Apply basic color correction based on analysis"""
    
    # Default correction values
    corrections = {
        'brightness': 0.02,
        'contrast': 1.05,
        'saturation': 1.0,
        'gamma': 1.0,
        'temperature': 0.0,
        'tint': 0.0
    }
    
    # Apply recommendations from analysis if available
    if analysis_data and 'recommendations' in analysis_data:
        corrections.update(analysis_data['recommendations'])
    
    print(f"🔧 Applying basic color correction...")
    print(f"Settings: {corrections}")
    
    await session.call_tool("apply_color_grading", {
        "input_path": input_path,
        "output_path": output_path,
        **corrections
    })
    
    print(f"✅ Basic correction applied: {output_path}")
    return output_path

# Usage
corrected_video = await basic_color_correction("raw_footage.mp4", "corrected.mp4", analysis)
```

### Step 3: Advanced Correction Techniques

For more precise control, use custom filters:

```python
async def advanced_color_correction(input_path: str, output_path: str):
    """Apply advanced color correction using custom filters"""
    
    # Advanced correction filter chain
    filter_chain = [
        "eq=brightness=0.02:contrast=1.05",           # Basic adjustments
        "colorbalance=rs=0.1:gs=0.0:bs=-0.1",        # Color balance
        "curves=m='0/0 0.25/0.22 0.5/0.55 0.75/0.8 1/1'",  # Tone curve
        "unsharp=5:5:0.3:5:5:0.0"                    # Subtle sharpening
    ]
    
    # Combine filters
    combined_filter = ",".join(filter_chain)
    
    await session.call_tool("apply_filter", {
        "input_path": input_path,
        "output_path": output_path,
        "filter_string": combined_filter
    })
    
    print(f"✅ Advanced correction applied: {output_path}")
    return output_path

# Usage
advanced_corrected = await advanced_color_correction("corrected.mp4", "advanced_corrected.mp4")
```

## 🎭 Creative Color Grading Styles

### Popular Cinematic Looks

#### 1. Cinematic/Film Look

```python
async def cinematic_grade(input_path: str, output_path: str):
    """Apply cinematic color grading for film-like appearance"""
    
    await session.call_tool("apply_color_grading", {
        "input_path": input_path,
        "output_path": output_path,
        "brightness": 0.0,
        "contrast": 1.15,      # Higher contrast
        "saturation": 0.9,     # Slightly desaturated
        "gamma": 1.1,          # Lifted gamma for film emulation
        "temperature": -0.15,  # Slightly warm
        "shadows": 0.1,        # Lifted shadows
        "highlights": -0.05    # Slightly crushed highlights
    })
    
    print("🎬 Cinematic grade applied")
    return output_path

# Usage
cinematic_video = await cinematic_grade("corrected.mp4", "cinematic.mp4")
```

#### 2. Modern Digital Look

```python
async def modern_digital_grade(input_path: str, output_path: str):
    """Apply modern, clean digital look"""
    
    await session.call_tool("apply_color_grading", {
        "input_path": input_path,
        "output_path": output_path,
        "brightness": 0.03,
        "contrast": 1.2,       # High contrast
        "saturation": 1.15,    # Vibrant colors
        "gamma": 0.95,         # Slightly lowered gamma
        "temperature": 0.1,    # Cool temperature
        "shadows": -0.02,      # Slightly crushed shadows
        "highlights": -0.03    # Controlled highlights
    })
    
    print("💎 Modern digital grade applied")
    return output_path
```

#### 3. Vintage/Retro Look

```python
async def vintage_grade(input_path: str, output_path: str):
    """Apply vintage/retro color grading"""
    
    # First apply color grading
    await session.call_tool("apply_color_grading", {
        "input_path": input_path,
        "output_path": "temp_vintage_grade.mp4",
        "brightness": 0.05,
        "contrast": 0.85,      # Lower contrast
        "saturation": 0.75,    # Desaturated
        "gamma": 1.2,          # Higher gamma
        "temperature": -0.3,   # Warm temperature
        "shadows": 0.15,       # Lifted shadows
        "highlights": -0.1     # Rolled off highlights
    })
    
    # Add vintage film effects
    vintage_filter = "curves=vintage,vignette=angle=PI/4,noise=alls=5:allf=t"
    
    await session.call_tool("apply_filter", {
        "input_path": "temp_vintage_grade.mp4",
        "output_path": output_path,
        "filter_string": vintage_filter
    })
    
    print("📼 Vintage grade applied")
    return output_path
```

#### 4. Teal and Orange Look

```python
async def teal_orange_grade(input_path: str, output_path: str):
    """Apply popular teal and orange Hollywood look"""
    
    # Custom filter for teal and orange
    teal_orange_filter = (
        "colorbalance=rs=0.2:gs=-0.1:bs=-0.3:rm=0.1:gm=0.0:bm=-0.2:rh=0.3:gh=0.1:bh=-0.1,"
        "eq=contrast=1.25:saturation=1.3"
    )
    
    await session.call_tool("apply_filter", {
        "input_path": input_path,
        "output_path": output_path,
        "filter_string": teal_orange_filter
    })
    
    print("🧡💚 Teal and orange grade applied")
    return output_path
```

### Custom Style Creation

```python
async def create_custom_style(input_path: str, output_path: str, style_config: dict):
    """Create custom color grade based on configuration"""
    
    style_name = style_config.get('name', 'Custom')
    print(f"🎨 Applying custom style: {style_name}")
    
    # Primary color grading
    primary_grade = style_config.get('primary_grade', {})
    
    if primary_grade:
        temp_file = "temp_primary_grade.mp4"
        await session.call_tool("apply_color_grading", {
            "input_path": input_path,
            "output_path": temp_file,
            **primary_grade
        })
        current_file = temp_file
    else:
        current_file = input_path
    
    # Secondary adjustments (custom filters)
    secondary_filters = style_config.get('secondary_filters', [])
    
    for i, filter_config in enumerate(secondary_filters):
        temp_file = f"temp_secondary_{i}.mp4"
        
        await session.call_tool("apply_filter", {
            "input_path": current_file,
            "output_path": temp_file,
            "filter_string": filter_config['filter']
        })
        
        current_file = temp_file
        print(f"  ✅ Applied filter {i+1}: {filter_config.get('name', 'Unknown')}")
    
    # Final output
    if current_file != output_path:
        await session.call_tool("trim_video", {
            "input_path": current_file,
            "output_path": output_path,
            "start_time": 0  # Copy entire video
        })
    
    print(f"✅ Custom style '{style_name}' applied: {output_path}")
    return output_path

# Example custom style configuration
dramatic_style = {
    "name": "Dramatic",
    "primary_grade": {
        "brightness": -0.02,
        "contrast": 1.3,
        "saturation": 1.1,
        "gamma": 1.15,
        "shadows": 0.08,
        "highlights": -0.1
    },
    "secondary_filters": [
        {
            "name": "Vignette",
            "filter": "vignette=angle=PI/3"
        },
        {
            "name": "Slight Blur",
            "filter": "gblur=sigma=0.5"
        }
    ]
}

# Usage
dramatic_video = await create_custom_style("corrected.mp4", "dramatic.mp4", dramatic_style)
```

## 🔄 Professional Grading Workflows

### Multi-Pass Grading Workflow

```python
async def professional_grading_workflow(input_path: str, final_output: str):
    """Complete professional color grading workflow"""
    
    print("🎬 Starting professional grading workflow...")
    
    # Pass 1: Technical Correction
    print("\n📐 Pass 1: Technical Correction")
    
    # Analyze footage
    analysis = await analyze_footage_for_correction(input_path)
    
    # Apply basic correction
    pass1_output = "pass1_corrected.mp4"
    await basic_color_correction(input_path, pass1_output, analysis)
    
    # Pass 2: Primary Grading
    print("\n🎨 Pass 2: Primary Grading")
    
    pass2_output = "pass2_primary.mp4"
    await session.call_tool("apply_color_grading", {
        "input_path": pass1_output,
        "output_path": pass2_output,
        "brightness": 0.01,
        "contrast": 1.12,
        "saturation": 1.05,
        "gamma": 1.05,
        "temperature": -0.05,
        "shadows": 0.03,
        "highlights": -0.02
    })
    
    # Pass 3: Secondary Grading (Creative Look)
    print("\n✨ Pass 3: Creative Grading")
    
    pass3_output = "pass3_creative.mp4"
    creative_filter = (
        "colorbalance=rs=0.05:gs=0.0:bs=-0.05,"
        "curves=r='0/0 0.5/0.58 1/1':g='0/0 0.5/0.52 1/1':b='0/0 0.5/0.48 1/1'"
    )
    
    await session.call_tool("apply_filter", {
        "input_path": pass2_output,
        "output_path": pass3_output,
        "filter_string": creative_filter
    })
    
    # Pass 4: Final Polish
    print("\n💎 Pass 4: Final Polish")
    
    polish_filter = (
        "unsharp=5:5:0.3:5:5:0.0,"  # Subtle sharpening
        "eq=gamma_r=1.02:gamma_g=1.0:gamma_b=0.98"  # Fine gamma adjustments
    )
    
    await session.call_tool("apply_filter", {
        "input_path": pass3_output,
        "output_path": final_output,
        "filter_string": polish_filter
    })
    
    print(f"\n✅ Professional grading complete: {final_output}")
    
    # Generate before/after comparison
    await create_before_after_comparison(input_path, final_output)
    
    return final_output

async def create_before_after_comparison(before_path: str, after_path: str):
    """Create side-by-side before/after comparison"""
    
    comparison_output = "before_after_comparison.mp4"
    
    # Create side-by-side comparison
    await session.call_tool("create_video_mosaic", {
        "input_paths": [before_path, after_path],
        "output_path": comparison_output,
        "layout": "1x2",  # Side by side
        "width": 1920,
        "height": 1080,
        "border_width": 4,
        "border_color": "white"
    })
    
    print(f"📊 Before/after comparison created: {comparison_output}")
    return comparison_output

# Usage
professional_graded = await professional_grading_workflow("raw_footage.mp4", "final_graded.mp4")
```

### Batch Grading for Consistency

```python
async def batch_color_grading(video_files: list, grading_style: str):
    """Apply consistent color grading to multiple videos"""
    
    # Define grading presets
    grading_presets = {
        "corporate": {
            "brightness": 0.02,
            "contrast": 1.08,
            "saturation": 0.95,
            "gamma": 1.02,
            "temperature": 0.05,
            "shadows": 0.02
        },
        "social_media": {
            "brightness": 0.05,
            "contrast": 1.2,
            "saturation": 1.25,
            "gamma": 0.98,
            "temperature": -0.1,
            "highlights": -0.03
        },
        "documentary": {
            "brightness": 0.01,
            "contrast": 1.05,
            "saturation": 0.9,
            "gamma": 1.08,
            "temperature": 0.0,
            "shadows": 0.05
        },
        "artistic": {
            "brightness": 0.0,
            "contrast": 1.25,
            "saturation": 0.8,
            "gamma": 1.15,
            "temperature": -0.2,
            "shadows": 0.1,
            "highlights": -0.08
        }
    }
    
    if grading_style not in grading_presets:
        raise ValueError(f"Unknown grading style: {grading_style}")
    
    preset = grading_presets[grading_style]
    print(f"🎨 Applying {grading_style} grading to {len(video_files)} videos")
    
    results = []
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_file}")
        
        try:
            output_file = f"{grading_style}_graded_{video_file}"
            
            await session.call_tool("apply_color_grading", {
                "input_path": video_file,
                "output_path": output_file,
                **preset
            })
            
            results.append({
                "input": video_file,
                "output": output_file,
                "status": "success"
            })
            
            print(f"  ✅ Graded: {output_file}")
            
        except Exception as e:
            results.append({
                "input": video_file,
                "output": None,
                "status": "error",
                "error": str(e)
            })
            
            print(f"  ❌ Error: {e}")
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n📊 Batch grading complete: {successful}/{len(video_files)} successful")
    
    return results

# Usage
video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
batch_results = await batch_color_grading(video_files, "social_media")
```

## 📊 Color Grading Analysis and QC

### Automated Quality Control

```python
async def color_grading_qc(graded_video: str, reference_video: str = None):
    """Perform quality control analysis on graded footage"""
    
    print(f"🔍 Performing QC analysis on: {graded_video}")
    
    # Extract video statistics
    stats = await session.call_tool("extract_video_statistics", {
        "input_path": graded_video,
        "include_quality_metrics": True
    })
    
    # Extract color information
    color_analysis = await session.call_tool("extract_dominant_colors", {
        "input_path": graded_video,
        "num_colors": 10,
        "sample_interval": 15.0
    })
    
    # QC Checks
    qc_issues = []
    qc_warnings = []
    
    # Check for extreme values
    if stats.get('brightness_avg', 0) > 0.8:
        qc_issues.append("Video may be overexposed")
    elif stats.get('brightness_avg', 0) < 0.2:
        qc_issues.append("Video may be underexposed")
    
    if stats.get('contrast_ratio', 1) > 3.0:
        qc_warnings.append("Very high contrast - may look unnatural")
    elif stats.get('contrast_ratio', 1) < 0.5:
        qc_warnings.append("Low contrast - may look flat")
    
    # Check color distribution
    dominant_color_count = len([c for c in color_analysis['dominant_colors'] 
                               if c['percentage'] > 15])
    
    if dominant_color_count < 2:
        qc_warnings.append("Limited color palette - may look monotonous")
    elif dominant_color_count > 6:
        qc_warnings.append("Very diverse color palette - may look chaotic")
    
    # Compare with reference if provided
    if reference_video:
        ref_colors = await session.call_tool("extract_dominant_colors", {
            "input_path": reference_video,
            "num_colors": 5
        })
        
        # Basic color difference check (simplified)
        print("📊 Color comparison with reference:")
        print("  (Detailed comparison would require more sophisticated analysis)")
    
    # Generate report
    print(f"\n📋 QC Report for {graded_video}:")
    
    if qc_issues:
        print(f"❌ Issues ({len(qc_issues)}):")
        for issue in qc_issues:
            print(f"  • {issue}")
    
    if qc_warnings:
        print(f"⚠️  Warnings ({len(qc_warnings)}):")
        for warning in qc_warnings:
            print(f"  • {warning}")
    
    if not qc_issues and not qc_warnings:
        print("✅ No issues detected - grading looks good!")
    
    return {
        "issues": qc_issues,
        "warnings": qc_warnings,
        "statistics": stats,
        "color_analysis": color_analysis
    }

# Usage
qc_report = await color_grading_qc("final_graded.mp4", "reference.mp4")
```

## 🎯 Advanced Techniques

### LUT (Look-Up Table) Simulation

```python
async def simulate_lut_application(input_path: str, output_path: str, lut_style: str):
    """Simulate LUT application using color grading parameters"""
    
    # Simulate popular LUT styles
    lut_simulations = {
        "kodak_5218": {
            "description": "Kodak Vision3 5218 film emulation",
            "brightness": 0.03,
            "contrast": 0.92,
            "saturation": 0.88,
            "gamma": 1.12,
            "temperature": -0.08,
            "shadows": 0.12,
            "highlights": -0.05,
            "custom_filter": "curves=vintage,colorbalance=rs=0.05:bs=-0.05"
        },
        "fuji_8543": {
            "description": "Fuji 8543 film emulation",
            "brightness": 0.02,
            "contrast": 0.95,
            "saturation": 0.92,
            "gamma": 1.08,
            "temperature": -0.12,
            "shadows": 0.08,
            "highlights": -0.03,
            "custom_filter": "colorbalance=rs=0.08:gs=0.02:bs=-0.08"
        },
        "alexa_rec709": {
            "description": "Arri Alexa to Rec709 conversion",
            "brightness": 0.01,
            "contrast": 1.05,
            "saturation": 1.02,
            "gamma": 1.0,
            "temperature": 0.02,
            "shadows": 0.02,
            "highlights": -0.02,
            "custom_filter": "eq=gamma_r=1.02:gamma_g=1.0:gamma_b=0.98"
        }
    }
    
    if lut_style not in lut_simulations:
        available_luts = ", ".join(lut_simulations.keys())
        raise ValueError(f"Unknown LUT style. Available: {available_luts}")
    
    lut_config = lut_simulations[lut_style]
    print(f"🎨 Applying LUT simulation: {lut_style}")
    print(f"Description: {lut_config['description']}")
    
    # Apply primary grading
    temp_file = "temp_lut_primary.mp4"
    primary_params = {k: v for k, v in lut_config.items() 
                     if k not in ['description', 'custom_filter']}
    
    await session.call_tool("apply_color_grading", {
        "input_path": input_path,
        "output_path": temp_file,
        **primary_params
    })
    
    # Apply custom filter if specified
    if 'custom_filter' in lut_config:
        await session.call_tool("apply_filter", {
            "input_path": temp_file,
            "output_path": output_path,
            "filter_string": lut_config['custom_filter']
        })
    else:
        # Copy to final output
        await session.call_tool("trim_video", {
            "input_path": temp_file,
            "output_path": output_path,
            "start_time": 0
        })
    
    print(f"✅ LUT simulation applied: {output_path}")
    return output_path

# Usage
lut_graded = await simulate_lut_application("corrected.mp4", "lut_graded.mp4", "kodak_5218")
```

## 🎯 Next Steps

You now have comprehensive knowledge of color grading with the VFX MCP Server! Continue your journey:

- **[VFX and Compositing](/guides/vfx-compositing/)** - Advanced visual effects
- **[Batch Processing](/guides/batch-processing/)** - Apply grading to multiple videos
- **[Common Workflows](/guides/common-workflows/)** - Complete production pipelines
- **[Visual Effects Examples](/examples/visual-effects/)** - Practical grading examples

**Want to explore more?** Check our [FAQ](/support/faq/) for common color grading questions or dive into the [tool reference](/tools/effects-filters/) for detailed parameter information.