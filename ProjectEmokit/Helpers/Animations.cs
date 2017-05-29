using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Animation;

namespace ProjectEmokit.Helpers
{
    public class Animations
    {
        public static void FadeOut(UIElement element, int miliseconds, bool collapse)
        {
            DoubleAnimation da = new DoubleAnimation();
            da.From = 1;
            da.To = 0;
            da.Duration = new Duration(TimeSpan.FromMilliseconds(miliseconds));
            if (collapse)
            {
                da.Completed += (s, e) =>
                {
                    element.Visibility = Visibility.Collapsed;
                };
            }
            element.BeginAnimation(Control.OpacityProperty, da);
        }

        public static void FadeOut(UIElement element, int miliseconds, bool collapse, Action completed)
        {
            DoubleAnimation da = new DoubleAnimation();
            da.From = 1;
            da.To = 0;
            da.Duration = new Duration(TimeSpan.FromMilliseconds(miliseconds));
            if (collapse)
            {
                da.Completed += (s, e) =>
                {
                    element.Visibility = Visibility.Collapsed;
                    completed();
                };
            }
            element.BeginAnimation(Control.OpacityProperty, da);
        }

        public static void FadeIn(UIElement element, int miliseconds)
        {
            element.Visibility = Visibility.Visible;
            DoubleAnimation da = new DoubleAnimation();
            da.From = 0;
            da.To = 1;
            da.Duration = new Duration(TimeSpan.FromMilliseconds(miliseconds));
            element.BeginAnimation(Control.OpacityProperty, da);
        }

        public async static void FadeOutIn(UIElement FOElement, int FODelay, UIElement FIElement, int FIDelay, int TransitionDelay, bool collapse)
        {
            FadeOut(FOElement, FODelay, collapse);
            await Task.Delay(TransitionDelay);
            FadeIn(FIElement, FIDelay);
        }

    }
}
