using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace ProjectEmokit.Models
{
    public class StageHelperModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public StageHelperModel()
        {
            CurrentStage = 0;
            PreviousStage = 0;
            CurrentSubStage = 0;
            PreviousSubStage = 0;
        }

        private int currentStage;
        public int CurrentStage
        {
            get { return currentStage; }
            set
            {
                currentStage = value;
                // Call OnPropertyChanged whenever the property is updated
                OnPropertyChanged("CurrentStage");
            }
        }
        private int currentSubStage;
        public int CurrentSubStage
        {
            get { return currentSubStage; }
            set
            {
                currentSubStage = value;
                // Call OnPropertyChanged whenever the property is updated
                OnPropertyChanged("CurrentSubStage");
            }
        }

        public int PreviousStage { get; set; }
        public int PreviousSubStage { get; set; }
        public UIElement CurrentElement { get; set; }
        public UIElement PreviousElement { get; set; }

        // Create the OnPropertyChanged method to raise the event
        protected void OnPropertyChanged(string name)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(name));
            }
        }
    }
}
