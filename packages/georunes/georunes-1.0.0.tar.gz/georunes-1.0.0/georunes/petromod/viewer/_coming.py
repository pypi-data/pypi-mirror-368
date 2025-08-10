from georunes.petromod.modelers.batch import BatchModeler
from georunes.petromod.modelers.partition import get_non_modal_dist_coeffs


class BatchNonModal(BatchModeler):  # todo implement
    def __init__(self, bulk_dist_coeffs, melt_propotions, part_coeffs):
        BatchModeler.__init__(self, bulk_dist_coeffs)
        self.nmod_dist_coeffs = get_non_modal_dist_coeffs(melt_propotions, part_coeffs)

    def ratio_liq(self, liq_fract):
        """
        Calculate the ratio : liquid / initial concentration
        """
        ratio_liq = 1 / (self.bulk_dist_coeffs + liq_fract * (1 - self.nmod_dist_coeffs))
        return ratio_liq

    def ratio_sol(self, liq_fract):
        """
        Calculate the ratio : solid / initial concentration
        """
        ratio_sol = self.bulk_dist_coeffs.copy()
        for index, row in ratio_sol.items():
            _part = (self.bulk_dist_coeffs[index] - liq_fract * self.nmod_dist_coeffs[index]) / (1 - liq_fract)
            ratio_sol[index] = _part / (self.bulk_dist_coeffs[index] + liq_fract * (1 - self.nmod_dist_coeffs[index]))
        return ratio_sol
