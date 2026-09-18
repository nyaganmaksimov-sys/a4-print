from pathlib import Path
import re

root = Path('buildsrc/A4PhotoID')

def read(p): return p.read_text(encoding='utf-8-sig')
def write(p,s): p.write_text(s, encoding='utf-8-sig')
def sub1(s, pat, repl, label, flags=0):
    out,n = re.subn(pat, repl, s, count=1, flags=flags)
    if n != 1: raise RuntimeError(f'{label}: replaced {n}')
    return out

# Version files
p=root/'src/A4PhotoID/A4PhotoID.csproj'; s=read(p)
s=s.replace('<Version>2.3.1</Version>','<Version>2.3.2</Version>')
s=s.replace('<AssemblyVersion>2.3.1.0</AssemblyVersion>','<AssemblyVersion>2.3.2.0</AssemblyVersion>')
s=s.replace('<FileVersion>2.3.1.0</FileVersion>','<FileVersion>2.3.2.0</FileVersion>')
write(p,s)
p=root/'installer/A4PhotoID.nsi'; s=read(p).replace('!define APP_VERSION "2.3.1"','!define APP_VERSION "2.3.2"'); write(p,s)
p=root/'build-installer.ps1'; s=read(p).replace('A4PhotoID_Setup_2.3.1_win-x64.exe','A4PhotoID_Setup_2.3.2_win-x64.exe'); write(p,s)

write(root/'src/A4PhotoID/Services/SettingsService.cs', '''using System.IO;\nusing System.Text.Json;\n\nnamespace A4PhotoID.Services;\n\npublic sealed class SettingsService\n{\n    private readonly string _settingsPath;\n\n    public SettingsService()\n    {\n        var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "A4PhotoID");\n        Directory.CreateDirectory(dir);\n        _settingsPath = Path.Combine(dir, "settings.json");\n    }\n\n    public string LoadSaveDirectory()\n    {\n        try\n        {\n            if (!File.Exists(_settingsPath)) return DefaultSaveDirectory();\n            var json = File.ReadAllText(_settingsPath);\n            var data = JsonSerializer.Deserialize<AppSettings>(json);\n            return string.IsNullOrWhiteSpace(data?.SaveDirectory) ? DefaultSaveDirectory() : data.SaveDirectory;\n        }\n        catch\n        {\n            return DefaultSaveDirectory();\n        }\n    }\n\n    public void SaveSaveDirectory(string? directory)\n    {\n        try\n        {\n            var value = string.IsNullOrWhiteSpace(directory) ? DefaultSaveDirectory() : directory.Trim();\n            var json = JsonSerializer.Serialize(new AppSettings { SaveDirectory = value }, new JsonSerializerOptions { WriteIndented = true });\n            File.WriteAllText(_settingsPath, json);\n        }\n        catch\n        {\n        }\n    }\n\n    private static string DefaultSaveDirectory() =>\n        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyPictures), "A4 PhotoID");\n\n    private sealed class AppSettings\n    {\n        public string SaveDirectory { get; set; } = string.Empty;\n    }\n}\n''')

p=root/'src/A4PhotoID/Services/ImageExportService.cs'; s=read(p)
s=sub1(s, r'public string SaveJpeg\\(BitmapSource source, string filePrefix\\)\\s*\\{.*?using var stream = File\\.Create\\(path\\);',
'''public string SaveJpeg(BitmapSource source, string filePrefix, string? destinationDirectory = null)
    {
        var safePrefix = string.Concat(filePrefix.Where(ch => !Path.GetInvalidFileNameChars().Contains(ch))).Trim();
        if (string.IsNullOrWhiteSpace(safePrefix)) safePrefix = "A4PhotoID";
        var directory = string.IsNullOrWhiteSpace(destinationDirectory)
            ? Environment.GetFolderPath(Environment.SpecialFolder.MyPictures)
            : destinationDirectory.Trim();
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, $"{safePrefix}_{DateTime.Now:yyyyMMdd_HHmmss}.jpg");
        using var stream = File.Create(path);''', 'image export', re.S)
write(p,s)

p=root/'src/A4PhotoID/Services/PrintLayoutService.cs'; s=read(p)
s=sub1(s, r'public string SaveJpeg\\(BitmapSource source\\)\\s*\\{.*?using var stream = File\\.Create\\(path\\);',
'''public string SaveJpeg(BitmapSource source, string? destinationDirectory = null)
    {
        var directory = string.IsNullOrWhiteSpace(destinationDirectory)
            ? Environment.GetFolderPath(Environment.SpecialFolder.MyPictures)
            : destinationDirectory.Trim();
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, $"A4PhotoID_sheet_{DateTime.Now:yyyyMMdd_HHmmss}.jpg");
        using var stream = File.Create(path);''', 'layout export', re.S)
write(p,s)

p=root/'src/A4PhotoID/ViewModels/MainViewModel.cs'; s=read(p)
s=s.replace('    private readonly JobHistoryService _jobHistoryService = new();','    private readonly JobHistoryService _jobHistoryService = new();\n    private readonly SettingsService _settingsService = new();')
s=s.replace('    private bool _cameraCaptureRunning;','    private bool _cameraCaptureRunning;\n    private string _saveDirectory = string.Empty;')
s=s.replace('''        LivePreviewButtonText = IsLivePreviewActive
            ? "Остановить видеоискатель"
            : SourceImage is not null
                ? "Видеоискатель / переснять"
                : "Видеоискатель";''','''        LivePreviewButtonText = IsLivePreviewActive
            ? "Остановить видеоискатель"
            : SourceImage is not null
                ? "Видеоискатель / новый снимок"
                : "Видеоискатель";''')
anchor='    public string FinalPhotoInfo { get => _finalPhotoInfo; private set => SetProperty(ref _finalPhotoInfo, value); }\n'
if anchor not in s: raise RuntimeError('FinalPhotoInfo anchor missing')
s=s.replace(anchor, anchor+'''    public string SaveDirectory
    {
        get => _saveDirectory;
        set
        {
            var normalized = string.IsNullOrWhiteSpace(value) ? _settingsService.LoadSaveDirectory() : value.Trim();
            if (!SetProperty(ref _saveDirectory, normalized)) return;
            _settingsService.SaveSaveDirectory(normalized);
        }
    }
''',1)
s=s.replace('    public ICommand ResetEditsCommand { get; }','    public ICommand ResetEditsCommand { get; }\n    public ICommand ResetCropCommand { get; }\n    public ICommand ResetCorrectionsCommand { get; }\n    public ICommand BrowseSaveDirectoryCommand { get; }',1)
s=s.replace('        _previewTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(90) };','        _previewTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(55) };',1)
s=s.replace('        SelectedBackgroundOption = BackgroundOptions[0];','        SelectedBackgroundOption = BackgroundOptions[0];\n        _saveDirectory = _settingsService.LoadSaveDirectory();\n        OnPropertyChanged(nameof(SaveDirectory));',1)
s=s.replace('        ResetEditsCommand = new RelayCommand(ResetEdits);','        ResetEditsCommand = new RelayCommand(ResetEdits);\n        ResetCropCommand = new RelayCommand(ResetCrop);\n        ResetCorrectionsCommand = new RelayCommand(ResetCorrections);\n        BrowseSaveDirectoryCommand = new RelayCommand(BrowseSaveDirectory);',1)

s=sub1(s, r'    private void ResetEdits\\(\\)\\s*\\{.*?\\n    \\}\\n\\n    private void ResetEditValues\\(bool resetFrame\\)',
'''    private void ResetEdits()
    {
        ResetEditValues(resetFrame: true);
        _autoCorrectionEnabled = false;
        OnPropertyChanged(nameof(AutoCorrectionEnabled));
        ClearAutoFrameMetrics("Автоустановка сброшена");
        RebuildPreview();
        Status = "Кадрирование и коррекция сброшены";
    }

    private void ResetCrop()
    {
        _zoom = 1.0;
        _offsetX = 0;
        _offsetY = 0;
        _rotationDegrees = 0;
        OnPropertyChanged(nameof(Zoom));
        OnPropertyChanged(nameof(OffsetX));
        OnPropertyChanged(nameof(OffsetY));
        OnPropertyChanged(nameof(RotationDegrees));
        RaiseEditorTransformProperties();
        ClearAutoFrameMetrics("Кадрирование сброшено");
        RebuildPreview();
        Status = "Кадрирование сброшено; цветовая коррекция сохранена";
    }

    private void ResetCorrections()
    {
        _autoCorrectionEnabled = false;
        _brightness = 0;
        _contrast = 0;
        _saturation = 0;
        _exposure = 0;
        _temperature = 0;
        _tint = 0;
        _shadows = 0;
        _highlights = 0;
        _sharpness = 0;
        OnPropertyChanged(nameof(AutoCorrectionEnabled));
        OnPropertyChanged(nameof(Brightness));
        OnPropertyChanged(nameof(Contrast));
        OnPropertyChanged(nameof(Saturation));
        OnPropertyChanged(nameof(Exposure));
        OnPropertyChanged(nameof(Temperature));
        OnPropertyChanged(nameof(Tint));
        OnPropertyChanged(nameof(Shadows));
        OnPropertyChanged(nameof(Highlights));
        OnPropertyChanged(nameof(Sharpness));
        MarkWorkingImageDirty();
        RebuildPreview();
        Status = "Цветовая коррекция сброшена; кадрирование сохранено";
    }

    private void BrowseSaveDirectory()
    {
        try
        {
            var dialog = new Microsoft.Win32.OpenFolderDialog
            {
                Title = "Выберите папку для сохранения фотографий A4 PhotoID",
                Multiselect = false
            };
            if (Directory.Exists(SaveDirectory)) dialog.InitialDirectory = SaveDirectory;
            if (dialog.ShowDialog() != true) return;
            SaveDirectory = dialog.FolderName;
            Status = $"Папка сохранения: {SaveDirectory}";
        }
        catch (Exception ex)
        {
            Status = $"Не удалось выбрать папку: {ex.Message}";
            MessageBox.Show(Status, "A4 PhotoID — папка сохранения", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    private void ResetEditValues(bool resetFrame)''', 'reset methods', re.S)

s=sub1(s, r'        // Clear the previous document only after the camera has successfully restarted\\..*?\\n    private async Task StopLivePreviewAsync\\(\\)',
'''        // Keep the last prepared photo, crop and print sheet while the operator uses the viewfinder.
        // They are replaced only after a NEW frame has actually been captured successfully.
        IsLivePreviewActive = true;
        CameraSummary = $"{SelectedCamera.DisplayName} • видеоискатель активен • предыдущая фотография сохранена";
        Status = SourceImage is null
            ? "Видеоискатель активен. Весь кадр камеры показан целиком. Двойной щелчок или «Снять» — сделать снимок."
            : "Видеоискатель активен. Предыдущая готовая фотография сохранена справа и будет заменена только после успешного нового снимка.";
    }

    private async Task StopLivePreviewAsync()''', 'preserve photo', re.S)

start=s.index('    private void SavePhoto()')
end=s.index('    private void SaveJob()',start)
newsave='''    private void SavePhoto()
    {
        if (FinalCroppedImage is null || SelectedTemplate is null) return;
        try
        {
            var prefix = $"{ClientName}_{SanitizeTemplateName(SelectedTemplate.Name)}";
            var path = _imageExportService.SaveJpeg(FinalCroppedImage, prefix, SaveDirectory);
            Status = $"Фото документа сохранено: {path}";
            MessageBox.Show($"Готовая фотография сохранена:\\n{path}", "A4 PhotoID", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
            Status = $"Не удалось сохранить фотографию: {ex.Message}";
            MessageBox.Show(Status, "A4 PhotoID — сохранение", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    private void SaveSheet()
    {
        if (SheetImage is null) return;
        try
        {
            _lastSheetPath = _layoutService.SaveJpeg(SheetImage, SaveDirectory);
            Status = $"Лист сохранён: {_lastSheetPath}";
            MessageBox.Show($"Готовый лист сохранён:\\n{_lastSheetPath}", "A4 PhotoID", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
            Status = $"Не удалось сохранить лист: {ex.Message}";
            MessageBox.Show(Status, "A4 PhotoID — сохранение", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

'''
s=s[:start]+newsave+s[end:]
write(p,s)

p=root/'src/A4PhotoID/MainWindow.xaml'; s=read(p)
s=s.replace('Title="A4 PhotoID 2.3.1" Height="960" Width="1600" MinHeight="820" MinWidth="1320"','Title="A4 PhotoID 2.3.2" Height="900" Width="1560" MinHeight="700" MinWidth="1320"',1)
s=s.replace('Text="A4 PhotoID 2.3.1"','Text="A4 PhotoID 2.3.2"',1)
s=s.replace('Text="A4 PhotoID 2.3.1 · Live View · фон · Photoshop"','Text="A4 PhotoID 2.3.2 · Live View · редактор · путь сохранения"',1)
s=s.replace('<RowDefinition x:Name="BottomActionsRow" Height="86"/>','<RowDefinition x:Name="BottomActionsRow" Height="128"/>',1)
s=s.replace('<ColumnDefinition Width="460"/>','<ColumnDefinition Width="430"/>',1)
s=s.replace('<RowDefinition x:Name="EditorControlsRow" Height="190"/>','<RowDefinition x:Name="EditorControlsRow" Height="176"/>',1)
s=s.replace('<Slider Minimum="-1" Maximum="1" Value="{Binding Brightness}" Margin="0,7,0,0"/>','<Slider Minimum="-2" Maximum="2" Value="{Binding Exposure, UpdateSourceTrigger=PropertyChanged}" Margin="0,7,0,0"/>',1)
for prop in ['Zoom','OffsetX','OffsetY','RotationDegrees','Exposure','Brightness','Contrast','Temperature','Tint','Saturation','Shadows','Highlights','Sharpness','CorrectionStrength','BackgroundTolerance','BackgroundFeather']:
    s=s.replace(f'Value="{{Binding {prop}}}"',f'Value="{{Binding {prop}, UpdateSourceTrigger=PropertyChanged}}"')
s=s.replace('IsChecked="{Binding AutoCorrectionEnabled}"','IsChecked="{Binding AutoCorrectionEnabled, UpdateSourceTrigger=PropertyChanged}"')
s=s.replace('IsChecked="{Binding RemoveBackgroundEnabled}"','IsChecked="{Binding RemoveBackgroundEnabled, UpdateSourceTrigger=PropertyChanged}"')
s=s.replace('Content="Сбросить кадрирование" Command="{Binding ResetEditsCommand}"','Content="Сбросить кадрирование" Command="{Binding ResetCropCommand}"',1)
s=s.replace('Content="Сбросить коррекцию" Command="{Binding ResetEditsCommand}"','Content="Сбросить коррекцию" Command="{Binding ResetCorrectionsCommand}"',1)
s=s.replace('<Button Grid.Column="0" Content="Добавить изображение" Command="{Binding LoadImageCommand}" Style="{StaticResource PrimaryButton}" Margin="0,0,4,0"/>','<Button Grid.Column="0" Content="Добавить" Command="{Binding LoadImageCommand}" Style="{StaticResource PrimaryButton}" Margin="0,0,4,0" ToolTip="Добавить изображение из файла"/>',1)
s=s.replace('<Button Grid.Column="1" Content="{Binding LivePreviewButtonText}" Command="{Binding ToggleLivePreviewCommand}" Style="{StaticResource SecondaryButton}" Margin="4,0,4,0" ToolTip="Включить видеоискатель. После готового кадра — начать новую съёмку / переснять."/>','<Button Grid.Column="1" Content="Видео" Command="{Binding ToggleLivePreviewCommand}" Style="{StaticResource SecondaryButton}" Margin="4,0,4,0" ToolTip="Включить/остановить видеоискатель. Предыдущее готовое фото сохраняется до нового снимка."/>',1)
s=s.replace('<Button Content="Сбросить" Command="{Binding ResetEditsCommand}" Style="{StaticResource SecondaryButton}"/>','<Button Content="Сбросить" Command="{Binding ResetCropCommand}" Style="{StaticResource SecondaryButton}"/>',1)
s=s.replace('Content="Сохранить JPEG" Command="{Binding SaveSheetCommand}"','Content="Сохранить лист" Command="{Binding SaveSheetCommand}"',1)
old='''                        <StackPanel Grid.Column="2">
                            <TextBlock Text="Быстрый источник / статус" Style="{StaticResource SectionTitle}"/>
                            <TextBlock Text="{Binding CameraSummary}" Foreground="{StaticResource MutedBrush}" FontSize="11" TextWrapping="Wrap"/>
                            <TextBlock Text="{Binding Status}" Foreground="{StaticResource MutedBrush}" FontSize="11" TextWrapping="Wrap" Margin="0,4,0,0"/>
                            <Grid Margin="0,8,0,0">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                </Grid.ColumnDefinitions>
                                <Button Grid.Column="0" Content="Обновить лист" Command="{Binding BuildSheetCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,4,0"/>
                                <Button Grid.Column="1" Content="Сохранить фото" Command="{Binding SavePhotoCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,4,0"/>
                                <Button Grid.Column="2" Content="Печать" Command="{Binding PrintCommand}" Style="{StaticResource PrimaryButton}"/>
                            </Grid>
                        </StackPanel>'''
new='''                        <Grid Grid.Column="2">
                            <Grid.RowDefinitions>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="Auto"/>
                                <RowDefinition Height="Auto"/>
                            </Grid.RowDefinitions>
                            <TextBlock Grid.Row="0" Text="Папка сохранения" FontWeight="SemiBold" Margin="0,0,0,4"/>
                            <Grid Grid.Row="1">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="86"/>
                                </Grid.ColumnDefinitions>
                                <TextBox Grid.Column="0" Text="{Binding SaveDirectory, UpdateSourceTrigger=LostFocus}" Height="30" Margin="0,0,6,0" ToolTip="Сюда сохраняются готовые фото и листы"/>
                                <Button Grid.Column="1" Content="Выбрать…" Command="{Binding BrowseSaveDirectoryCommand}" Style="{StaticResource SecondaryButton}" Height="30" Padding="6,2"/>
                            </Grid>
                            <Grid Grid.Row="2" Margin="0,6,0,0">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                </Grid.ColumnDefinitions>
                                <Button Grid.Column="0" Content="Обновить лист" Command="{Binding BuildSheetCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,4,0" Height="32"/>
                                <Button Grid.Column="1" Content="Сохранить фото" Command="{Binding SavePhotoCommand}" Style="{StaticResource SecondaryButton}" Margin="0,0,4,0" Height="32"/>
                                <Button Grid.Column="2" Content="Печать" Command="{Binding PrintCommand}" Style="{StaticResource PrimaryButton}" Height="32"/>
                            </Grid>
                        </Grid>'''
if old not in s: raise RuntimeError('bottom status block not found')
s=s.replace(old,new,1)
write(p,s)

p=root/'src/A4PhotoID/MainWindow.xaml.cs'; s=read(p)
s=s.replace('''    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainViewModel();
    }''','''    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainViewModel();
        Loaded += (_, _) => FitWindowToWorkArea();
    }

    private void FitWindowToWorkArea()
    {
        var area = SystemParameters.WorkArea;
        MaxWidth = Math.Max(MinWidth, area.Width);
        MaxHeight = Math.Max(MinHeight, area.Height);
        Width = Math.Min(Width, Math.Max(MinWidth, area.Width - 8));
        Height = Math.Min(Height, Math.Max(MinHeight, area.Height - 8));
        if (Left < area.Left) Left = area.Left;
        if (Top < area.Top) Top = area.Top;
    }''',1)
s=s.replace('BottomActionsRow.Height = enabled ? new GridLength(0) : new GridLength(86);','BottomActionsRow.Height = enabled ? new GridLength(0) : new GridLength(128);',1)
s=s.replace('EditorControlsRow.Height = enabled ? new GridLength(0) : new GridLength(190);','EditorControlsRow.Height = enabled ? new GridLength(0) : new GridLength(176);',1)
write(p,s)

print('A4 PhotoID 2.3.2 patch applied.')
