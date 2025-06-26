import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AttackComponent } from './attack/attack.component';
import { EvaluationComponent } from './evaluation/evaluation.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { CustomComponent } from './custom/custom.component';
import { PathComponent } from './path/path.component';
import { DataComponent } from './data/data.component';

export const routes: Routes = [
    {path: '', component: HomeComponent},
    {path: 'attack', component: AttackComponent},
    {path: 'evaluation', component: EvaluationComponent},
    {path: 'configuration', component: ConfigurationComponent},
    {path: 'custom', component: CustomComponent},
    {path: 'config', component: ConfigurationComponent},
    {path: 'path', component: PathComponent},
    {path: 'data', component: DataComponent}
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})

export class AppRoutesModule {}