using Microsoft.AspNet.SignalR.Client;
using Microsoft.AspNet.SignalR.Client.Transports;
using ProjectEmokit.Helpers;
using ProjectEmokit.Models;
using ProjectEmokit.Python;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace ProjectEmokit
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        #region Initialize
        private Dictionary<UIElement, int> AllStages { get; set; }
        private StageHelperModel StageHelper { get; set; }
        public Dictionary<string, List<string>> EmokitOptions { get; set; }
        private bool IsServerConnected { get; set; }
        public IHubProxy EmokitHub { get; set; }
        public PythonProcesses pythonProcess { get; set; }
        public bool EmokitStarted { get; set; }
        public bool EmokitStopped { get; set; }
        #endregion

        #region Initialize methods
        private void LoadAllStages()
        {
            AllStages = new Dictionary<UIElement, int>
            {
                { LoadingPanel, -1 },
                { InitialEmokit, 0 },
                { ControlEmokit, 1 },
                { SettingsEmokit, 2 }
            };
        }
        private void LoadEmokitOptions()
        {
            EmokitOptions = new Dictionary<string, List<string>>
            {
                { "Please select", new List<string>() { "Please select" } },
                { "Read", new List<string> { "Please select", "Save Encrypted Data (fast)", "Save Decrypted Data (slow)" } },
                { "Decrypt", new List<string>() { "Please select" } }
            };
        }
        private void LoadSettings()
        {
            CommandPrompt.Text = StaticVariables.COMMAND_PROMPT;
            PythonApplication.Text = StaticVariables.PYTHON_APP;
            PythonEEGAppPath.Text = StaticVariables.PYTHON_EEG_PATH;
            PythonEEGDecryptPath.Text = StaticVariables.DECRYPT_EEG_PATH;
            PythonEEGApp.Text = StaticVariables.EEG_APP;
            RunPythonEEG.Text = StaticVariables.PYTHON_EEG;
            ServerURL.Text = StaticVariables.ServerURL;
            ServerHub.Text = StaticVariables.EmokitHub;
        }
        private async void ConnectToEmokitServer(bool tryAgain)
        {
            IStatus.Text = "Connecting to the server";
            try
            {
                var hubConnection = new HubConnection(StaticVariables.ServerURL);
                EmokitHub = hubConnection.CreateHubProxy(StaticVariables.EmokitHub);
                EmokitHub.On<string>("OnProducerChanged", OnProducerChanged);
                await hubConnection.Start(new LongPollingTransport());

                // start the emokit server
                IsServerConnected = true;
                IStatus.Text = "Connected to the server";
                await Task.Delay(100);
                await EmokitHub.Invoke<bool>("Stop");
                if (tryAgain)
                    StartPythonApp();
            }
            catch (Exception)
            {
                IsServerConnected = false;
                IStatus.Text = "Failed to connect";
                SetStage(InitialEmokit, LoadingPanel);
            }
        }
        private void Initialize()
        {
            LoadAllStages();
            StageHelper = new StageHelperModel();
            StageHelper.PropertyChanged += StageHelper_PropertyChanged;
            StaticVariables.SetStaticVariables();
            LoadSettings();
            LoadEmokitOptions();
            ConnectToEmokitServer(false);
            DataContext = this;
        }
        #endregion

        #region Common Methods
        private void SetStage(UIElement currentElement, UIElement previousElement)
        {
            StageHelper.PreviousElement = previousElement;
            StageHelper.CurrentElement = currentElement;
            StageHelper.PreviousStage = AllStages[previousElement];
            StageHelper.CurrentStage = AllStages[currentElement];
        }

        private List<string> GetFilesToDecrypt()
        {
            var customDecryptFiles = new List<string>();
            var filePath = StaticVariables.DECRYPT_EEG_PATH;
            if (Directory.Exists(filePath))
            {
                customDecryptFiles.Add("Please select");
                DirectoryInfo directoryInfo = new DirectoryInfo(filePath);
                foreach (var directories in directoryInfo.GetDirectories())
                {
                    // Get info on Decrypt and Encrypt folders
                    DirectoryInfo directoryEncryptInfo = new DirectoryInfo(directories.FullName + @"\encrypt");
                    // Check if there are files to decrypt
                    if (directoryEncryptInfo.GetFiles().Count() > 0)
                    {
                        DirectoryInfo directoryDecryptInfo = new DirectoryInfo(directories.FullName + @"\decrypt");
                        // Check if it is already decrypted
                        if (directoryDecryptInfo.GetFiles().Count() == 0)
                        {
                            if (!Directory.Exists(directories.FullName + @"\custom"))
                                customDecryptFiles.Add(directories.Name);
                        }
                    }

                }
            }
            return customDecryptFiles;
        }

        private void UpdateIQuestion2()
        {
            if (IQuestion1.SelectedIndex == 2)
                EmokitOptions["Decrypt"] = GetFilesToDecrypt();
            IQuestion2.ItemsSource = EmokitOptions[((KeyValuePair<string, List<string>>)IQuestion1.SelectedValue).Key];
            IQuestion2.SelectedIndex = 0;
        }

        private void StartPythonApp()
        {
            if (IQuestion1.SelectedIndex > 0 & IQuestion2.SelectedIndex > 0)
            {
                var arguments = " " + ((KeyValuePair<string, List<string>>)IQuestion1.SelectedValue).Key;
                if (IQuestion1.SelectedIndex == 1)
                {
                    if (IQuestion2.SelectedIndex == 1)
                        arguments += " " + "True False";
                    else arguments += " " + "False True";
                }
                else arguments += " " + StaticVariables.DECRYPT_EEG_PATH.Replace(" ", "SPACE") + @"\" + IQuestion2.SelectedValue;
                SetStage(LoadingPanel, InitialEmokit);
                pythonProcess = new PythonProcesses();
                pythonProcess.StartPythonEEG(arguments);
            }
        }
        #endregion

        public MainWindow()
        {
            InitializeComponent();
            Initialize();
        }

        #region Events
        private void OnProducerChanged(string value)
        {
            Application.Current.Dispatcher.Invoke(new Action(async () =>
            {
                await Task.Delay(2000);
                switch (value)
                {
                    case "init":
                        if (IQuestion1.SelectedIndex == 2)
                        {
                            UpdateIQuestion2();
                            await EmokitHub.Invoke<bool>("Stop");
                        }
                        else
                        {
                            IStatus.Text = "";
                            CStatus.Text = "Please check the Python console if it received the 'init'";
                            SetStage(ControlEmokit, LoadingPanel);
                        }
                        break;
                    case "start":
                        CButton.Content = "Stop";
                        CStatus.Text = "Close the console after saving completes. 'Initialize' will start a new process while saving!!";
                        SetStage(ControlEmokit, LoadingPanel);
                        break;
                    case "stop":
                        CButton.Content = "Start";
                        SetStage(InitialEmokit, LoadingPanel);
                        break;
                    default:
                        break;
                }
            }));
        }

        private async void StageHelper_PropertyChanged(object sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == "CurrentStage")
            {
                var stage = sender as StageHelperModel;

                if (stage.CurrentStage >= -1)
                {
                    Application.Current.Dispatcher.Invoke(new Action(() =>
                    {
                        if (stage.CurrentStage == -1)
                            MainNavigation.Visibility = Visibility.Collapsed;
                        else MainNavigation.Visibility = Visibility.Visible;

                        Animations.FadeOutIn(stage.PreviousElement, 500, stage.CurrentElement, 500, 1000, true);
                    }));                   
                    await Task.Delay(2000);
                }
            }
        }

        private void IQuestion1_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateIQuestion2();
        }

        private void IButton_Click(object sender, RoutedEventArgs e)
        {
            if (IsServerConnected)
                StartPythonApp();
            else
                ConnectToEmokitServer(true);
        }

        private async void CButton_Click(object sender, RoutedEventArgs e)
        {
            SetStage(LoadingPanel, ControlEmokit);
            if((string)CButton.Content == "Start")
                await EmokitHub.Invoke<bool>("Start");
            else await EmokitHub.Invoke<bool>("Stop");
        }

        private void MainNavigation_Click(object sender, RoutedEventArgs e)
        {
            if ((string)MainNavigation.Content == "")
            {
                MainNavigation.Content = "";
                SetStage(SettingsEmokit, AllStages.FirstOrDefault(x => x.Value == StageHelper.CurrentStage).Key);
            }
            else
            {
                MainNavigation.Content = "";
                SetStage(StageHelper.PreviousElement, SettingsEmokit);
            }
        }
        #endregion
    }
}
