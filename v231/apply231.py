from pathlib import Path

root = Path('buildsrc/A4PhotoID')


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig')


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8-sig')


def replace_required(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual < count:
        raise RuntimeError(f'{label}: expected at least {count} occurrence(s), found {actual}')
    return text.replace(old, new, count)

# Version metadata.
csproj = root / 'src/A4PhotoID/A4PhotoID.csproj'
t = read(csproj)
t = replace_required(t, '<Version>2.3.0</Version>', '<Version>2.3.1</Version>', 'csproj Version')
t = replace_required(t, '<AssemblyVersion>2.3.0.0</AssemblyVersion>', '<AssemblyVersion>2.3.1.0</AssemblyVersion>', 'csproj AssemblyVersion')
t = replace_required(t, '<FileVersion>2.3.0.0</FileVersion>', '<FileVersion>2.3.1.0</FileVersion>', 'csproj FileVersion')
write(csproj, t)

nsi = root / 'installer/A4PhotoID.nsi'
t = read(nsi)
t = replace_required(t, '!define APP_VERSION "2.3.0"', '!define APP_VERSION "2.3.1"', 'NSIS version')
write(nsi, t)

build = root / 'build-installer.ps1'
t = read(build)
t = replace_required(t, 'A4PhotoID_Setup_2.3.0_win-x64.exe', 'A4PhotoID_Setup_2.3.1_win-x64.exe', 'installer filename')
write(build, t)

# Live View layout: camera stream is full-frame Uniform, document guide is a separate overlay.
xaml = root / 'src/A4PhotoID/MainWindow.xaml'
t = read(xaml)
t = replace_required(t, 'Title="A4 PhotoID 2.2"', 'Title="A4 PhotoID 2.3.1"', 'window title')
t = replace_required(t, 'Text="A4 PhotoID 2.2"', 'Text="A4 PhotoID 2.3.1"', 'header version')
t = replace_required(t, 'Text="A4 PhotoID 2.2 · Live View · фон · Photoshop"', 'Text="A4 PhotoID 2.3.1 · Live View · фон · Photoshop"', 'footer version')
t = replace_required(
    t,
    '<Button Grid.Column="1" Content="Снять с камеры" Command="{Binding CaptureFromCameraCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,8,0"/>',
    '<Button Grid.Column="1" Content="{Binding LivePreviewButtonText}" Command="{Binding ToggleLivePreviewCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,8,0" ToolTip="Открыть видеоискатель; после готового кадра — переснять."/>',
    'top camera button')
t = replace_required(
    t,
    '<Button Grid.Column="1" Content="{Binding LivePreviewButtonText}" Command="{Binding ToggleLivePreviewCommand}" Style="{StaticResource SecondaryButton}" Margin="4,0,4,0"/>',
    '<Button Grid.Column="1" Content="{Binding LivePreviewButtonText}" Command="{Binding ToggleLivePreviewCommand}" Style="{StaticResource SecondaryButton}" Margin="4,0,4,0" ToolTip="Включить видеоискатель. После готового кадра — начать новую съёмку / переснять."/>',
    'bottom live button')
t = replace_required(
    t,
    '<Image Source="{Binding EditorImage}" Stretch="UniformToFill" IsHitTestVisible="False"/>',
    '<Image Source="{Binding EditorImage}" Stretch="Uniform" IsHitTestVisible="False"/>',
    'secondary camera preview')

old_editor = '''                                    <!-- The working image is physically placed UNDER one fixed crop frame.
                                         FinalCroppedImage is rendered separately and is never simulated by this overlay. -->
                                    <Viewbox Stretch="Uniform" HorizontalAlignment="Center" VerticalAlignment="Center" Margin="34" IsHitTestVisible="False">
                                        <Grid Width="{Binding GuideWidth}" Height="{Binding GuideHeight}" ClipToBounds="True" Background="#0B1018">
                                            <Border Background="White" ClipToBounds="True">
                                                <Image Source="{Binding EditorImage}" Stretch="UniformToFill" RenderTransformOrigin="0.5,0.5">'''
new_editor = '''                                    <!-- Live View and photo editing are intentionally separate.
                                         Live View always shows the COMPLETE camera frame with Stretch=Uniform.
                                         The document guide is a transparent overlay and never clips the camera stream. -->
                                    <Grid IsHitTestVisible="False">
                                        <Grid.Style>
                                            <Style TargetType="Grid">
                                                <Setter Property="Visibility" Value="Collapsed"/>
                                                <Style.Triggers>
                                                    <DataTrigger Binding="{Binding IsLivePreviewActive}" Value="True">
                                                        <Setter Property="Visibility" Value="Visible"/>
                                                    </DataTrigger>
                                                </Style.Triggers>
                                            </Style>
                                        </Grid.Style>

                                        <Image Source="{Binding LiveCameraImage}" Stretch="Uniform"
                                               HorizontalAlignment="Stretch" VerticalAlignment="Stretch"/>

                                        <Viewbox Stretch="Uniform" HorizontalAlignment="Center" VerticalAlignment="Center" Margin="34">
                                            <Grid Width="{Binding GuideWidth}" Height="{Binding GuideHeight}" Background="Transparent">
                                                <Border BorderBrush="#66C8FF" BorderThickness="2.2" Background="#06000000"/>
                                                <Border Width="1.5" Background="#65B9FF" HorizontalAlignment="Center" Opacity="0.8"/>
                                                <Border Height="1.5" Background="#65B9FF" VerticalAlignment="Center" Opacity="0.45"/>
                                                <Border Height="2" Background="#F2C94C" VerticalAlignment="Top" Margin="{Binding GuideEyeLineMargin}" Opacity="0.95"/>
                                                <Ellipse Stroke="#4DD17A" StrokeThickness="2.3" Width="{Binding GuideHeadWidth}" Height="{Binding GuideHeadHeight}"
                                                         HorizontalAlignment="Center" VerticalAlignment="Top" Margin="{Binding GuideHeadMargin}" Fill="#0500FF00"/>
                                                <Border VerticalAlignment="Top" HorizontalAlignment="Left" Margin="8" Background="#B3121824" CornerRadius="10" Padding="8,4">
                                                    <TextBlock Text="{Binding GuideCaption}" Foreground="White" FontSize="10.5" FontWeight="SemiBold"/>
                                                </Border>
                                            </Grid>
                                        </Viewbox>
                                    </Grid>

                                    <!-- After capture the working image moves UNDER the fixed crop frame.
                                         FinalCroppedImage is rendered separately and is never simulated by this overlay. -->
                                    <Viewbox Stretch="Uniform" HorizontalAlignment="Center" VerticalAlignment="Center" Margin="34" IsHitTestVisible="False">
                                        <Viewbox.Style>
                                            <Style TargetType="Viewbox">
                                                <Setter Property="Visibility" Value="Visible"/>
                                                <Style.Triggers>
                                                    <DataTrigger Binding="{Binding IsLivePreviewActive}" Value="True">
                                                        <Setter Property="Visibility" Value="Collapsed"/>
                                                    </DataTrigger>
                                                </Style.Triggers>
                                            </Style>
                                        </Viewbox.Style>
                                        <Grid Width="{Binding GuideWidth}" Height="{Binding GuideHeight}" ClipToBounds="True" Background="#0B1018">
                                            <Border Background="White" ClipToBounds="True">
                                                <Image Source="{Binding WorkingImage}" Stretch="UniformToFill" RenderTransformOrigin="0.5,0.5">'''
t = replace_required(t, old_editor, new_editor, 'main Live View editor block')
write(xaml, t)

# View model: reliable restart + explicit retake state.
vm = root / 'src/A4PhotoID/ViewModels/MainViewModel.cs'
t = read(vm)
t = replace_required(t, 'private string _livePreviewButtonText = "Live View";', 'private string _livePreviewButtonText = "Видеоискатель";', 'initial Live View label')
t = replace_required(
    t,
    '''            OnPropertyChanged(nameof(EditorImage));
            OnPropertyChanged(nameof(EditorHint));
        }
    }

    // Backward-compatible name used by the existing camera and UI code.''',
    '''            OnPropertyChanged(nameof(EditorImage));
            OnPropertyChanged(nameof(EditorHint));
            UpdateLivePreviewButtonText();
        }
    }

    // Backward-compatible name used by the existing camera and UI code.''',
    'OriginalImage button-state update')
t = replace_required(
    t,
    '''            if (!SetProperty(ref _isLivePreviewActive, value)) return;
            LivePreviewButtonText = value ? "Остановить Live" : "Live View";
            OnPropertyChanged(nameof(EditorImage));''',
    '''            if (!SetProperty(ref _isLivePreviewActive, value)) return;
            UpdateLivePreviewButtonText();
            OnPropertyChanged(nameof(EditorImage));''',
    'Live View state setter')
t = replace_required(
    t,
    '''    public string LivePreviewButtonText { get => _livePreviewButtonText; private set => SetProperty(ref _livePreviewButtonText, value); }
    public string PhotoshopStatus { get => _photoshopStatus; private set => SetProperty(ref _photoshopStatus, value); }''',
    '''    public string LivePreviewButtonText { get => _livePreviewButtonText; private set => SetProperty(ref _livePreviewButtonText, value); }
    public string PhotoshopStatus { get => _photoshopStatus; private set => SetProperty(ref _photoshopStatus, value); }

    private void UpdateLivePreviewButtonText()
    {
        LivePreviewButtonText = IsLivePreviewActive
            ? "Остановить видеоискатель"
            : SourceImage is not null
                ? "Видеоискатель / переснять"
                : "Видеоискатель";
    }''',
    'dynamic Live View button label')
t = t.replace('var error = await _livePreviewService.StartAsync(SelectedCamera);', 'var error = await StartSelectedLivePreviewAsync();', 2)
if t.count('var error = await StartSelectedLivePreviewAsync();') < 2:
    raise RuntimeError('Live View start replacement failed')
t = replace_required(
    t,
    '''    private async Task ToggleLivePreviewAsync()
    {''',
    '''    private async Task<string?> StartSelectedLivePreviewAsync()
    {
        if (SelectedCamera is null) return "Камера не выбрана.";

        var error = await _livePreviewService.StartAsync(SelectedCamera);
        if (error is null) return null;

        // Some DSLR/UVC drivers keep the device busy briefly after preview capture stops.
        // Retry once so the operator can return to the viewfinder without restarting A4 PhotoID.
        await Task.Delay(450);
        return await _livePreviewService.StartAsync(SelectedCamera);
    }

    private async Task ToggleLivePreviewAsync()
    {''',
    'Live View retry helper')
t = replace_required(
    t,
    '''        IsLivePreviewActive = true;
        CameraSummary = $"{SelectedCamera.DisplayName} • Live View активен • первый двойной щелчок — снимок";
        Status = "Live View активен. Первый двойной щелчок делает снимок; второй двойной щелчок по снимку кадрирует его по размеру документа.";
    }

    private async Task StopLivePreviewAsync()''',
    '''        // Clear the previous document only after the camera has successfully restarted.
        // If opening the camera fails, the operator keeps the already prepared photo.
        ClearCapturedPhotoForNewShot();
        IsLivePreviewActive = true;
        CameraSummary = $"{SelectedCamera.DisplayName} • видеоискатель активен • двойной щелчок — новый снимок";
        Status = "Видеоискатель активен. Весь кадр камеры показан целиком. Двойной щелчок или кнопка «Снять» делает новый снимок.";
    }

    private void ClearCapturedPhotoForNewShot()
    {
        if (SourceImage is null) return;

        SourceImage = null;
        _lastSheetPath = null;
        ResetEditValues(resetFrame: true);
        QualityMessages.Clear();
        ClearAutoFrameMetrics("Новый снимок • совместите лицо с разметкой и снимите кадр");
        FaceStatus = "Видеоискатель активен. Двойной щелчок — сделать новый снимок";
        SheetInfo = "Лист 10×15 будет сформирован после нового снимка";
        FinalPhotoInfo = "Готовая фотография ещё не сформирована";
        OnPropertyChanged(nameof(EditorHint));
    }

    private async Task StopLivePreviewAsync()''',
    'retake state reset')
write(vm, t)

print('A4 PhotoID 2.3.1 Live View + retake patch applied.')
